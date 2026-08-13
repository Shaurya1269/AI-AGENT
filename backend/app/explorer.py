from .parser import parse_function, parse_import, parse_function_calls
from pathlib import Path


def get_functions(project_index):
    functions = []
    for file_path, content in project_index.items():
        for line_number, line_text in content:
            metadata = parse_function(line_text)

            if metadata:
                functions.append({
                    "file_path": str(file_path),
                    "line_number": line_number,
                    "name": metadata["name"]
                })
    return functions


def get_imports(project_index):
    imports = []
    for file_path, content in project_index.items():
        for line_number, line_text in content:
            print(repr(line_text))
            metadata = parse_import(line_text)
            if metadata:
                imports.append({
                    "file_path": str(file_path),
                    "line_number": line_number,
                    "module": metadata["module"],
                    "symbol": metadata["symbol"]
                })
    return imports


# where is the function created and where is it used
def find_definitions(project_index, symbol):
    definitions = []
    for file_path, content in project_index.items():
        for line_number, line_text in content:
            metadata = parse_function(line_text)
            if metadata and metadata["name"] == symbol:
                definitions.append({
                    "symbol": metadata["name"],
                    "file_path": str(file_path),
                    "line_number": line_number,
                })
    return definitions


def find_references(project_index, symbol):
    references = []
    for file_path, content in project_index.items():
        for line_number, line_text in content:
            if symbol in line_text:
                metadata = parse_function(line_text)
                if metadata and metadata["name"] == symbol:
                    continue
                else:
                    references.append({
                        "name": symbol,
                        "file_path": str(file_path),
                        "line_number": line_number,
                        "text": line_text.strip()
                    })
    return references


def get_function_body(file_content, file_path, function_name):
    # checking with the help of indentation level of function and using ennumerate
    for index, (line_number, line_text) in enumerate(file_content[file_path]):
        metadata = parse_function(line_text)
        if metadata and metadata["name"] == function_name:
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
    all_functions = get_functions(project_index)
    project_funtion_names = {function["name"] for function in all_functions}
    for line in function_body.splitlines():
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
    context = {
        "definition": definition,
        "body": body,
        "references": references,
        "imports": imports,
        "calls": calls
    }
    return context
