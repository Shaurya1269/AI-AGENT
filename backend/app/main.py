from fastapi import FastAPI
from pathlib import Path
from .scanner import scan_directory
from .search import search_index
from .explorer import (get_functions, get_imports,
                       find_definitions, find_references, get_function_body)
from .ai import answer_question

app = FastAPI()

# whenever someone performs get request on the root endpoint, this function will be executed


@app.get("/")
def root():
    return {"message": "Welcome to Shaurya's Antigravity"}


@app.get("/health")
def health():     # this endpoint is used to check the health of the application
    return {"status": "healthy", "services": "antigravity", "version": "1.0.0"}


project_index = {}


@app.get("/scan")
def scan():
    project = Path(".")
    global project_index
    project_index = scan_directory(project)
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


@app.get("/functions")
def functions():
    if not project_index:
        return {"status": "error",
                "message": "No files indexed. Please run the /scan endpoint first."}
    result = get_functions(project_index)
    return {
        "status": "success",
        "functions": result,
        "count": len(result)
    }


@app.get("/imports")
def imports():
    if not project_index:
        return {"status": "error",
                "message": "No files indexed. Please run the /scan endpoint first."}
    result = get_imports(project_index)
    return {
        "status": "success",
        "imports": result,
        "count": len(result)
    }


# tells us about the number of all the files,functions,imports,root files etc.
def get_projects():
    root = Path(".").resolve()  # gives absolute path
    project_structure = {
        "files": len(project_index),
        "functions": len(get_functions(project_index)),
        "imports": len(get_imports(project_index)),
        "python_files": 0,
        "text_files": len(project_index),
        "project_root": str(root)
    }
    for file_path in project_index:
        if file_path.suffix == ".py":
            project_structure["python_files"] += 1
    return project_structure


@app.get("/project")
def projects():
    if not project_index:
        return {"status": "error",
                "message": "No files indexed. Please run the /scan endpoint first."}
    result = get_projects()
    return {
        "status": "success",
        "project_structure": result
    }


@app.get("/definitions")
def definition(symbol: str):
    if not project_index:
        return {"status": "error",
                "message": "No files indexed. Please run the /scan endpoint first."}
    result = find_definitions(project_index, symbol)
    if not result:
        return {
            "status": "error",
            "message": f"No definition found for {symbol}."
        }
    return {
        "status": "success",
        "definition": result,
        "count": len(result)
    }


@app.get("/references")
def references(symbol: str):
    if not project_index:
        return {"status": "error",
                "message": "No files indexed. Please run the /scan endpoint first."}
    result = find_references(project_index, symbol)
    if not result:
        return {
            "status": "error",
            "message": f"No references found for {symbol}."
        }
    return {
        "status": "success",
        "references": result,
        "count": len(result)
    }


@app.get("/function_body")
def function_body(file_path: str, symbol: str):
    if not project_index:
        return {"status": "error",
                "message": "No files indexed. Please run the /scan endpoint first."}
    path = Path(file_path)
    if path not in project_index:
        return {"status": "error",
                "message": f"File {file_path} not found in the indexed files."}
    result = get_function_body(project_index, path, symbol)
    if not result:
        return {
            "status": "error",
            "message": f"No function body found for {symbol} in {file_path}."
        }
    return {
        "status": "success",
        "function_body": result
    }


@app.get("/ask")
def ask(symbol: str, question: str):
    if not project_index:
        return {
            "status": "error",
            "message": "No files indexed. Please run the /scan endpoint first."
        }
    result = answer_question(project_index, symbol, question)
    return {
        "status": "success",
        "symbol": symbol,
        "question": question,
        "answer": result
    }
