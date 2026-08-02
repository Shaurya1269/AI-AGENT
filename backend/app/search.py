from .parser import parse_function, parse_import

# shows the files in which the search term is found


def search_index(file_content, search_term):
    results = []
    # .items() returns a view object that displays a list of a dictionary's key-value tuple pairs.
    for file_path, content in file_content.items():
        for line_number, line_text in content:
            if search_term.lower() in line_text.lower():
                result = {
                    "file_path": str(file_path),
                    "line_number": line_number,
                    # strip() removes any leading and trailing whitespace characters from the string
                    "text": line_text.strip()
                }
                metadata = parse_function(line_text)
                if metadata is None:
                    metadata = parse_import(line_text)
                if metadata:
                    result.update(metadata)
                results.append(result)
    return results


