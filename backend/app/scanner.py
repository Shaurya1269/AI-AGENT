

ignore = {".venv",
          ".git",
          "__pycache__",
          "node_modules"}
def scan_directory(path):
    not_allowed_extensions = ('.png', '.jpg', '.jpeg', '.exe', '.zip')

    file_content = {}
    for item in path.iterdir():
        if item.name in ignore:
            continue
        elif item.is_dir():
            # update file_conte for each file found in the directory
            file_content.update(scan_directory(item))
        else:
            if item.name.endswith(not_allowed_extensions):
                continue
            else:
                file_content[item] = read_file(item)
    return file_content


def read_file(path):
    with open(path, "r") as file:
        # enumerate returns a tuple containing the index and the value of each item in the iterable
        content = list(enumerate(file.readlines(), start=1))
    return content