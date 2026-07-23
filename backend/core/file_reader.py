from pathlib import Path

project = Path(".")

for item in project.iterdir():
    print(item)
