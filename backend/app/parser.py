import re


def parse_function(line_text):  # checks if the line contains a function definition
    line = line_text.strip()
    match = re.match(r"(?:async\s+)?def\s+([A-Za-z_]\w*)\s*\(", line)
    if not match:
        return None
    return {
        "type": "function",
        "name": match.group(1)
    }


def parse_import(line_text):
    line = line_text.strip()
    from_match = re.match(r"from\s+([^\s]+)\s+import\s+(.+)", line)
    import_match = re.match(r"import\s+([^\s]+)", line)
    if from_match:
        module = from_match.group(1)
        symbol = from_match.group(2).split(",")[0].strip()
    elif import_match:
        module = import_match.group(1).rstrip(",")
        symbol = None
    else:
        return None
    return {
        "type": "import",
        "module": module,
        "symbol": symbol
    }


def parse_function_calls(line_text):
    line = line_text.strip()
    # matches looks like :
    matches = re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\(', line)
    if matches:
        return [
            {
                "type": "function_call",
                "name": name
            }
            for name in matches
        ]
    return []
