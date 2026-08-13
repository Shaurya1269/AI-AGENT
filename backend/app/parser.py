import re


def parse_function(line_text):  # checks if the line contains a function definition
    line = line_text.strip()
    if not line.startswith("def "):
        return None
    name = line.split("(")[0].replace("def ", "").strip()
    return {
        "type": "function",
        "name": name
    }


def parse_import(line_text):
    line = line_text.strip()
    if line.startswith("from"):
        module = line.split()[1]
        symbol = line.split()[3]
    elif line.startswith("import"):
        parts = line.split()
        if len(parts) > 1:
            module = line.split()[1]
            symbol = None
        else:
            return None

    else:
        return None
    return {
        "type": "import",
        "module": module,
        "symbol": symbol
    }


def parse_function_calls(line_text):
    line = line_text.strip()
    matches  = re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\(', line)  #matches looks like : 
    if matches:
        return [
        {
            "type": "function_call",
            "name" : name
        }
        for name in matches   
        ]
    return []

