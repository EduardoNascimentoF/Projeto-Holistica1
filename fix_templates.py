"""Script para atualizar as chamadas url_for nos templates HTML para usar o namespace do blueprint 'main'."""
import os
import glob

templates_dir = r'c:\Users\zrnfr\Documents\Holistica real\templates'
for filepath in glob.glob(os.path.join(templates_dir, '*.html')):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    replacements = {
        "url_for('login')": "url_for('main.login')",
        "url_for('home')": "url_for('main.home')",
        "url_for('tasks')": "url_for('main.tasks')",
        "url_for('reuniao')": "url_for('main.reuniao')",
        "url_for('metas')": "url_for('main.metas')",
        "url_for('funcionarios')": "url_for('main.funcionarios')",
        "url_for('registro')": "url_for('main.registro')",
        "url_for('logout')": "url_for('main.logout')",
        'url_for("login")': 'url_for("main.login")',
        'url_for("home")': 'url_for("main.home")',
        'url_for("tasks")': 'url_for("main.tasks")',
        'url_for("reuniao")': 'url_for("main.reuniao")',
        'url_for("metas")': 'url_for("main.metas")',
        'url_for("funcionarios")': 'url_for("main.funcionarios")',
        'url_for("registro")': 'url_for("main.registro")',
        'url_for("logout")': 'url_for("main.logout")',
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
print('Updated templates')
