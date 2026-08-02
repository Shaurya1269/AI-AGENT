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
