import re

from .ast_parser import build_ast_index, parse_python_variables
from pathlib import Path
from .parser import parse_function, parse_function_calls
from .scanner import scan_directory


def get_functions(project_index):
    ast_index = build_ast_index(project_index)
    functions = []
    for file_path, analysis in ast_index.items():
        for function in analysis["functions"]:
            functions.append({
                "file_path": str(file_path),
                "name": function["name"],
                "line_number": function["line_number"]
            })
    return functions


def get_imports(project_index):
    ast_index = build_ast_index(project_index)
    imports = []
    for file_path, analysis in ast_index.items():
        for item in analysis["imports"]:
            imports.append({
                "type": item["type"],
                "module": item["module"],
                "symbol": item["symbol"],
                "line_number": item["line_number"]
            })
    return imports


# where is the function created and where is it used
def find_definitions(project_index, symbol):
    ast_index = build_ast_index(project_index)
    definitions = []
    for file_path, analysis in ast_index.items():

        # for top level and nested functions
        for function in analysis["functions"]:
            if function["name"] == symbol:
                definitions.append({
                    "symbol": symbol,
                    "file_path": str(file_path),
                    "line_number": function["line_number"],
                    "type": "function"
                })

    # for classes
        for class_info in analysis["classes"]:
            if class_info["name"] == symbol:
                definitions.append({
                    "symbol": symbol,
                    "file_path": str(file_path),
                    "line_number": class_info["line_number"],
                    "type": "class"
                })

    # Methods inside classes
            for method in class_info["methods"]:
                if method["name"] == symbol:
                    definitions.append({
                        "symbol": symbol,
                        "file_path": str(file_path),
                        "line_number": method["line_number"],
                        "type": "method",
                        "class": class_info["name"]
                    })

    return definitions


def find_references(project_index, symbol):
    references = []
    symbol_pattern = re.compile(rf"\b{re.escape(symbol)}\b")
    for file_path, content in project_index.items():
        for line_number, line_text in content:
            stripped_line = line_text.strip()
            function_match = re.match(
                r"(?:async\s+)?def\s+([A-Za-z_]\w*)", stripped_line
            )
            class_match = re.match(r"class\s+([A-Za-z_]\w*)", stripped_line)
            is_definition = (
                (function_match and function_match.group(1) == symbol)
                or (class_match and class_match.group(1) == symbol)
            )
            if symbol_pattern.search(line_text) and not is_definition:
                references.append({
                    "name": symbol,
                    "file_path": str(file_path),
                    "line_number": line_number,
                    "text": stripped_line
                })
    return references


def get_function_body(file_content, file_path, function_name):
    # checking with the help of indentation level of function and using ennumerate
    for index, (line_number, line_text) in enumerate(file_content[file_path]):
        metadata = parse_function(line_text)
        stripped_line = line_text.strip()
        async_match = re.match(
            r"async\s+def\s+([A-Za-z_]\w*)\s*\(", stripped_line)
        if (metadata and metadata["name"] == function_name) or (
                async_match and async_match.group(1) == function_name):
            function_body = []
            indentation_level = len(line_text) - len(line_text.lstrip())
            function_body.append(line_text)
            for next_line_number, next_line_number_text in file_content[file_path][index+1:]:
                next_indentation_level = len(
                    next_line_number_text) - len(next_line_number_text.lstrip())
                if next_indentation_level <= indentation_level and next_line_number_text.strip() != "":
                    break
                function_body.append(next_line_number_text)
            return "".join(function_body)
    return None


def find_function_calls(project_index, function_body):
    calls = []
    if not function_body:
        return calls
    all_functions = get_functions(project_index)
    project_funtion_names = {function["name"] for function in all_functions}
    for line in function_body.splitlines():
        line = line.strip()
        if line.startswith("def "):
            continue
        parsed_calls = parse_function_calls(line)

        for call in parsed_calls:
            if call["name"] in project_funtion_names:
                calls.append(call["name"])

    return calls


def build_context(project_index, symbol):
    definition = find_definitions(project_index, symbol)
    if not definition:
        return None
    file_path = Path(definition[0]["file_path"])
    body = get_function_body(project_index, file_path, symbol)
    references = find_references(project_index, symbol)
    imports = get_imports(project_index)
    calls = find_function_calls(project_index, body)
    called_function_context = get_called_function_context(project_index, calls)
    variables = get_variable_context(project_index, body)
    context = {
        "definition": definition,
        "body": body,
        "references": references,
        "imports": imports,
        "calls": calls,
        "called_functions": called_function_context,
        "variables": variables
    }
    return context


def get_called_function_context(project_index, calls):
    called_functions = {}
    for call in calls:
        definition = find_definitions(project_index, call)

        if definition:
            file_path = Path(definition[0]["file_path"])
            body = get_function_body(project_index, file_path, call)
            calls_by_called_function = find_function_calls(project_index, body)
            called_functions[call] = {
                "definition": definition[0],
                "body": body,
                "calls": calls_by_called_function
            }
    return called_functions


def find_variable_definitions(project_index, symbol):
    variables = []

    for file_path, content in project_index.items():
        source_code = "".join(line_text for _, line_text in content)

        parsed_variables = parse_python_variables(source_code)

        for variable in parsed_variables:
            if variable["name"] == symbol:
                variables.append({
                    "name": variable["name"],
                    "file_path": str(file_path),
                    "line_number": variable["line_number"]
                })

    return variables


def get_variable_context(project_index, function_body):
    variables = {}

    # find variable names used inside function
    for file_path, content in project_index.items():
        source_code = "".join(line_text for _, line_text in content)
        parsed_variables = parse_python_variables(source_code)

        for variable in parsed_variables:
            name = variable["name"]
            if name in function_body:
                variables[name] = {
                    "definition": variable,
                    "file_path": str(file_path)
                }
    return variables


def find_relevant_symbols(project_index, question):
    relevant_symbols = []
    functions = get_functions(project_index)
    question_words = set(question.lower().split())

    for function in functions:
        name = function["name"].lower()

        if name in question_words:
            relevant_symbols.append(function["name"])

    return relevant_symbols


if __name__ == "__main__":
    project = Path(__file__).resolve().parents[2]

    project_index = scan_directory(project)

    print(
        find_relevant_symbols(
            project_index,
            "What directories does scan_directory ignore?"

        )
    )
