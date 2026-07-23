from importlib.resources import files

from fastapi import FastAPI
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
    file_content = {}
    for file in scan_directory(path):
        # making key value pair for file name and its content
        file_content[file] = read_files(file)
    return file_content

    # for item in path.iterdir():
    #     if item.name in ignore:
    #         continue
    #     elif item.is_dir():
    #         files.extend(scan_directory(item))
    #     else:
    #         files.append(item.name)
    # return files


def read_files(path):
    with open(path, "r") as file:
        content = file.read()
    return content
