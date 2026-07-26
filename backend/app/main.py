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
    not_allowed_entensions = ('.png', '.jpg', '.jpeg', '.exe', '.zip')

    file_content = {}
    for item in path.iterdir():
        if item.name in ignore:
            continue
        elif item.is_dir():
            # update file_conte for each file found in the directory
            file_content.update(scan_directory(item))
        else:
            if item.name.endswith(not_allowed_entensions):
                continue
            else:
                file_content[item] = read_file(item)
    return file_content


def read_file(path):
    with open(path, "r") as file:
        content = file.read()
    return content


# @app.get("/scan")
# def scan():
#     from pathlib import Path

#     project = Path(".")

#     result = scan_directory(project)

#     return {
#         "files": len(result)
#     }
