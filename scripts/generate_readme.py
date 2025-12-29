import os
import re

COURSES_START = "<!-- COURSES_START -->"
COURSES_END = "<!-- COURSES_END -->"
GAMES_START = "<!-- GAMES_START -->"
GAMES_END = "<!-- GAMES_END -->"

# Carpetas o archivos a excluir
EXCLUDE = {".git", ".github", "scripts", "__pycache__", ".vscode", ".env", "nore"}

def read_info(folder):
    """Lee info.txt si existe, si no devuelve cadena vacía"""
    info_path = os.path.join(folder, "info.txt")
    if os.path.exists(info_path):
        try:
            return open(info_path, encoding="utf-8").read().strip()
        except:
            return ""  # Si hay algún error, devolvemos vacío
    return ""  # Si no existe info.txt devolvemos vacío

def count_scripts(folder):
    """Cuenta solo los scripts .py visibles y válidos"""
    try:
        return len([
            f for f in os.listdir(folder)
            if f.endswith(".py") and not f.startswith("_") and f not in EXCLUDE
        ])
    except FileNotFoundError:
        return 0

def is_valid_folder(folder):
    """Devuelve True si la carpeta es válida"""
    name = os.path.basename(folder)
    if name in EXCLUDE:
        return False
    if name.startswith(".") or name.startswith("__"):
        return False
    return True

def get_courses():
    courses = []
    for d in os.listdir("."):
        if d.startswith("CursoPython") and os.path.isdir(d) and is_valid_folder(d):
            # Intentamos extraer número para ordenar
            nums = re.findall(r"\d+", d)
            number = int(nums[0]) if nums else 0
            courses.append((number, d))
    courses.sort(key=lambda x: x[0])
    return [d for _, d in courses]

def get_games():
    if not os.path.isdir("Juegos"):
        return []
    return sorted([
        d for d in os.listdir("Juegos")
        if os.path.isdir(os.path.join("Juegos", d)) and is_valid_folder(d)
    ])

def generate_section(items, base_path=""):
    lines = []
    for item in items:
        path = os.path.join(base_path, item).replace("\\", "/")
        scripts = count_scripts(path)
        if scripts == 0:
            continue  # No mostramos carpetas vacías de scripts
        info = read_info(path)
        # Creamos enlace clicable, y solo mostramos info si existe
        if info:
            lines.append(f"- 📁 **[{item}]({path})** ({scripts} scripts)  \n  {info}\n")
        else:
            lines.append(f"- 📁 **[{item}]({path})** ({scripts} scripts)\n")
    return "\n".join(lines)

# Leer README actual
with open("README.md", encoding="utf-8") as f:
    content = f.read()

# Generar secciones
courses_md = generate_section(get_courses())
games_md = generate_section(get_games(), "Juegos")

# Reemplazar secciones en README
content = re.sub(
    f"{COURSES_START}.*?{COURSES_END}",
    f"{COURSES_START}\n{courses_md}\n{COURSES_END}",
    content,
    flags=re.S
)

content = re.sub(
    f"{GAMES_START}.*?{GAMES_END}",
    f"{GAMES_START}\n{games_md}\n{GAMES_END}",
    content,
    flags=re.S
)

# Guardar README actualizado
with open("README.md", "w", encoding="utf-8") as f:
    f.write(content)

print("✔ README actualizado con cursos y juegos y enlaces (robusto)")
