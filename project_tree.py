from pathlib import Path


def print_tree(
    directory: Path,
    prefix: str = "",
    is_last: bool = True,
):
    connector = "└── " if is_last else "├── "
    print(prefix + connector + directory.name + ("/" if directory.is_dir() else ""))

    if directory.is_dir():
        children = sorted(
            directory.iterdir(),
            key=lambda x: (x.is_file(), x.name.lower())
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
        root.iterdir(),
        key=lambda x: (x.is_file(), x.name.lower())
    )

    for index, child in enumerate(children):
        is_last = index == len(children) - 1
        print_tree(child, "", is_last)


if __name__ == "__main__":
    project_root = r"C:\vitech_project\agentic-vitechq-copilot"

    generate_project_tree(project_root)