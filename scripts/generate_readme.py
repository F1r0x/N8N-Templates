import os
import re

# ========= CONFIGURACIÓN =========
INDEX_START = "<!-- INDEX_START -->"
INDEX_END = "<!-- INDEX_END -->"

EXCLUDE_DIRS = {
    ".git", ".github", "scripts", "__pycache__", ".vscode", "node_modules", ".env"
}

EXCLUDE_FILES = {
    ".gitignore"
}

ALLOWED_EXTENSIONS = {
    ".md", ".txt", ".pdf", ".py", ".sh", ".json"
}

MAX_DEPTH = 3

# ========= FUNCIONES =========

def is_valid_dir(name):
    return name not in EXCLUDE_DIRS and not name.startswith(".") and not name.startswith("__")

def is_valid_file(name, full_path):
    # Excluir SOLO el README.md raíz
    root_readme = os.path.abspath("README.md")
    current_file = os.path.abspath(full_path)
    if name.lower() == "readme.md" and current_file == root_readme:
        return False
    if name in EXCLUDE_FILES:
        return False
    _, ext = os.path.splitext(name)
    return ext.lower() in ALLOWED_EXTENSIONS

def scan_directory(base=".", depth=0):
    if depth > MAX_DEPTH:
        return []

    items = []

    try:
        entries = sorted(os.listdir(base))
    except PermissionError:
        return []

    folder_items = []

    for entry in entries:
        full_path = os.path.join(base, entry)
        rel_path = full_path.replace("\\", "/").lstrip("./")

        if os.path.isdir(full_path):
            if not is_valid_dir(entry):
                continue
            sub_items = scan_directory(full_path, depth + 1)
            if sub_items:
                folder_items.append((depth, f"📁 **[{entry}]({rel_path})**"))
                folder_items.extend(sub_items)

        elif os.path.isfile(full_path):
            if not is_valid_file(entry, full_path):
                continue
            # Para archivos JSON con iconos, Markdown y demás
            folder_items.append((depth, f"📄 [{entry}]({rel_path})"))

    if folder_items:
        items.extend(folder_items)

    return items

def build_markdown(items):
    lines = []
    for depth, text in items:
        indent = "  " * depth
        lines.append(f"{indent}- {text}")
    return "\n".join(lines)

# ========= ACTUALIZAR README =========
with open("README.md", encoding="utf-8") as f:
    content = f.read()

index_items = scan_directory()
index_md = build_markdown(index_items)

pattern = re.compile(f"{INDEX_START}.*?{INDEX_END}", flags=re.S)
replacement = f"{INDEX_START}\n{index_md}\n{INDEX_END}"

if pattern.search(content):
    content = pattern.sub(replacement, content)
else:
    content += f"\n\n{replacement}\n"

with open("README.md", "w", encoding="utf-8") as f:
    f.write(content)

print("✔ README actualizado con índice global incluyendo JSON y archivos especiales")
