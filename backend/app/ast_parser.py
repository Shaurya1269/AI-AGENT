# normal parser uses weak logic using strong comparing, this version uses ast - using nodes in the file as its logic
import ast


def parse_python_functions(source_code):
    tree = ast.parse(source_code)

    functions = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append({
                "type": "function",
                "name": node.name,
                "line_number": node.lineno,
                "end_line_number": node.end_lineno,
                "parameters": [
                    arg.arg for arg in node.args.args
                ]
            })
    return functions


def parse_python_imports(source_code):
    tree = ast.parse(source_code)

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({
                    "type": "import",
                    "module": alias.name,
                    "symbol": None,
                    "line_number": node.lineno
                })

        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports.append({
                    "type": "import",
                    "module": ("." * node.level) + (node.module or ""),
                    "symbol": alias.name,
                    "line_number": node.lineno
                })

    return imports


def parse_python_calls(source_code):
    tree = ast.parse(source_code)

    calls = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            else:
                continue
            calls.append({
                "type": "function_call",
                "name": name,
                "line_number": node.lineno
            })
    return calls


def parse_python_classes(source_code):
    tree = ast.parse(source_code)
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = []
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append({
                        "name": child.name,
                        "line_number": child.lineno,
                        "end_line_number": child.end_lineno
                    })
            classes.append({
                "type": "class",
                "name": node.name,
                "line_number": node.lineno,
                "end_line_number": node.end_lineno,
                "methods": methods
            })
    return classes


def analyze_python(source_code):
    return {
        "functions": parse_python_functions(source_code),
        "imports": parse_python_imports(source_code),
        "calls": parse_python_calls(source_code),
        "classes": parse_python_classes(source_code)
    }


def build_ast_index(project_index):
    ast_index = {}

    for file_path, content in project_index.items():
        if file_path.suffix.lower() != ".py":
            continue
        source_code = "".join(
            # line_text is the text of each line in the file, _ is the line number
            line_text for _, line_text in content
        )
        ast_index[file_path] = analyze_python(source_code)
    return ast_index


def parse_python_variables(source_code):
    tree = ast.parse(source_code)

    variables = []

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variables.append({
                        "type": "variable",
                        "name": target.id,
                        "line_number": node.lineno,
                        "value": ast.unparse(node.value)
                    })

    return variables


if __name__ == "__main__":
    source = """
ignore = {".venv", ".git", "__pycache__", "node_modules"}

def scan_directory(path):
    if path in ignore:
        return
"""

    print(parse_python_variables(source))
