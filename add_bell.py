""" SINO DE NOTIFICAÇÃO (PRECISO MELHORAR ISSO DPS, MAS FOI PRA TESTE) """
import os

bell_html = """
                <!-- Bell Icon -->
                <div style="position: relative; margin-right: 15px; cursor: pointer; display: flex; align-items: center;" onclick="window.location.href='/notificacoes'">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: white;">
                        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                        <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                    </svg>
                    {% if notificacoes_nao_lidas > 0 %}
                    <span style="position: absolute; top: -5px; right: -5px; background: #ff4a4a; color: white; font-size: 10px; font-weight: bold; width: 16px; height: 16px; display: flex; align-items: center; justify-content: center; border-radius: 50%;">{{ notificacoes_nao_lidas }}</span>
                    {% endif %}
                </div>
"""

templates_dir = r"c:\Users\zrnfr\Documents\Holistica real\templates"
files = ["home.html", "perfil.html", "tasks.html", "reuniao.html", "metas.html", "funcionarios.html"]

for f in files:
    path = os.path.join(templates_dir, f)
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()
    
    if "<!-- Bell Icon -->" not in content:
        content = content.replace('<div class="topo-direita">', f'<div class="topo-direita" style="display: flex; align-items: center;">\n{bell_html}')
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
