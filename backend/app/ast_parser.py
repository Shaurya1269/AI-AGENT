# normal parser uses weak logic using strong comparing, this version uses ast - using nodes in the file as its logic
import ast


def parse_functions(source_code):
    tree = ast.parse(source_code)

    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
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
                    "module": node.module,
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
                        "name" : child.name,
                        "line_number": child.lineno,
                        "end_line_number": child.end_lineno
                    })
            classes.append({
                "type" : "class",
                "name" : node.name,
                "line_number" : node.lineno,
                "end_line_number" : node.end_lineno,
                "methods" : methods
            })
    return classes
            
            
source = """
class Scanner:
    def scan(self):
        pass

    def read(self):
        pass


class Database:
    def connect(self):
        pass
"""

print(parse_python_classes(source))           