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
                "parameters":[
                    arg.arg for arg in node.args.args
                ] 
            })
    return functions


if __name__ == "__main__":
    code = """
def outer():
    def inner():
        return 10

    return inner()
"""

    result = parse_functions(code)

    print(result)
