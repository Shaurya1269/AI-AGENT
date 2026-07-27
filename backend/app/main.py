from fastapi import FastAPI
from pathlib import Path
app = FastAPI()


# whenever someone performs get request on the root endpoint, this function will be executed
@app.get("/")
def root():
    return {"message": "Welcome to Shaurya's Antigravity"}


@app.get("/health")
def health():     # this endpoint is used to check the health of the application
    return {"status": "healthy", "services": "antigravity", "version": "1.0.0"}


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


project_index = {}


@app.get("/scan")
def scan():
    project = Path(".")
    global project_index
    project_index = (scan_directory(project))
    return {
        "status": "success",
        "indexed_files": f"{len(project_index)} "
    }


@app.get("/search")
def search(search_term):
    if search_term is None or search_term.strip() == "":
        return {"status": "error", "message": "Search term cannot be empty."}
    elif not project_index:
        return {"status": "error", "message": "No files indexed. Please run the /scan endpoint first."}

    result = search_index(project_index, search_term)
    return {
        "status": "success",
        "matches": result,
        "count": len(result)
    }


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
        module = line.split()[1]
        symbol = None

    else:
        return None
    return {
        "type": "import",
        "module_": module,
        "symbol": symbol
    }
