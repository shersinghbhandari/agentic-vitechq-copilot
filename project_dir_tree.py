from pathlib import Path
import sys


def print_tree(
    directory: Path,
    prefix: str = "",
    is_last: bool = True,
):
    connector = "└── " if is_last else "├── "

    print(prefix + connector + directory.name + "/")

    children = sorted(
        [
            child for child in directory.iterdir()
            if child.is_dir()
        ],
        key=lambda x: x.name.lower()
    )

    new_prefix = prefix + ("    " if is_last else "│   ")

    for index, child in enumerate(children):
        is_child_last = index == len(children) - 1
        print_tree(child, new_prefix, is_child_last)


def generate_project_tree(root_path: str):
    root = Path(root_path)

    if not root.exists():
        print(f"Directory does not exist: {root_path}")
        return

    print(root.name + "/")

    children = sorted(
        [
            child for child in root.iterdir()
            if child.is_dir()
        ],
        key=lambda x: x.name.lower()
    )

    for index, child in enumerate(children):
        is_last = index == len(children) - 1
        print_tree(child, "", is_last)


if __name__ == "__main__":
    project_root = r"C:\vitech_project\agentic-vitechq-copilot\backend"

    generate_project_tree(project_root)