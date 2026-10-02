"""Script para atualizar automaticamente as URLs em routes.py para usar o namespace do blueprint 'main'."""
import os

routes_path = r'c:\Users\zrnfr\Documents\Holistica real\routes.py'
with open(routes_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    'url_for("login")': 'url_for("main.login")',
    'url_for("home")': 'url_for("main.home")',
    'url_for("tasks")': 'url_for("main.tasks")',
    'url_for("reuniao")': 'url_for("main.reuniao")',
    'url_for("metas")': 'url_for("main.metas")',
    'url_for("funcionarios")': 'url_for("main.funcionarios")',
    'url_for("registro")': 'url_for("main.registro")',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(routes_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated routes.py')
