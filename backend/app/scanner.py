ignore = {".venv",
          ".git",
          "__pycache__",
          "node_modules"}

not_allowed_extensions = {".png", ".jpg", ".jpeg", ".exe", ".zip"}


def scan_directory(path):
    file_content = {}
    for item in path.iterdir():
        if item.name in ignore:
            continue
        elif item.is_dir() and not item.is_symlink():
            file_content.update(scan_directory(item))
        else:
            if item.suffix.lower() in not_allowed_extensions:
                continue
            file_content[item] = read_file(item)
    return file_content


def read_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as file:
        # enumerate returns a tuple containing the index and the value of each item in the iterable
        content = list(enumerate(file.readlines(), start=1))
    return content
