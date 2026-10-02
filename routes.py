import calendar
import os
from datetime import datetime, date

# pyrefly: ignore [missing-import]
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory
# pyrefly: ignore [missing-import]
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, Usuario, Tarefa, Reuniao, FuncionarioDoMes, Evento, DashboardGlobal, Notificacao

bp = Blueprint('main', __name__)

@bp.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(bp.root_path, 'static', 'images'),
        'logo.jpeg',
        mimetype='image/jpeg'
    )

@bp.app_context_processor
def inject_user_data():
    if "usuario_logado" in session:
        user = Usuario.query.filter_by(username=session["usuario_logado"]).first()
        todos_usuarios = Usuario.query.all()  # Changed to all users so ADM is included
        
        notifs_count = 0
        if user:
            if user.cargo == "ADM":
                notifs_count = Notificacao.query.filter_by(usuario_id=None, lida=False).count()
            else:
                notifs_count = Notificacao.query.filter_by(usuario_id=user.id, lida=False).count()
                
        return dict(current_user=user, todos_usuarios=todos_usuarios, notificacoes_nao_lidas=notifs_count)
    return dict(current_user=None, todos_usuarios=[], notificacoes_nao_lidas=0)


@bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario_digitado = request.form.get("username")
        senha_digitada = request.form.get("password")
        user = Usuario.query.filter_by(username=usuario_digitado).first()

        if user and check_password_hash(user.senha_hash, senha_digitada):
            session["usuario_logado"] = user.username
            session["cargo_usuario"] = user.cargo
            return redirect(url_for("main.home"))

        return render_template("index.html", erro="Usuário ou senha incorretos!")

    return render_template("index.html")




@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@bp.route("/home")
def home():
    if "usuario_logado" not in session:
        return redirect(url_for("main.login"))
    return render_template("home.html")


@bp.route("/perfil", methods=["GET", "POST"])
def perfil():
    if "usuario_logado" not in session:
        return redirect(url_for("main.login"))
    
    user = Usuario.query.filter_by(username=session["usuario_logado"]).first()
    
    if request.method == "POST":
        novo_nome = request.form.get("nome_exibicao")
        nova_foto = request.form.get("foto_perfil")
        nova_bio = request.form.get("bio")

        if novo_nome:
            user.nome_exibicao = novo_nome
        if nova_foto:
            user.foto_perfil = nova_foto
        if nova_bio is not None:
            user.bio = nova_bio

        db.session.commit()
        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for("main.perfil"))
        
    return render_template("perfil.html", current_user=user)


@bp.route("/notificacoes")
def notificacoes():
    if "usuario_logado" not in session:
        return redirect(url_for("main.login"))
        
    user = Usuario.query.filter_by(username=session["usuario_logado"]).first()
    
    if user.cargo == "ADM":
        notifs = Notificacao.query.filter_by(usuario_id=None).order_by(Notificacao.id.desc()).all()
    else:
        notifs = Notificacao.query.filter_by(usuario_id=user.id).order_by(Notificacao.id.desc()).all()
        
    for n in notifs:
        n.lida = True
    db.session.commit()
    
    return render_template("notificacoes.html", notificacoes=notifs)



@bp.route("/tasks", methods=["GET", "POST"])
def tasks():
    if "usuario_logado" not in session:
        return redirect(url_for("main.login"))

    user = Usuario.query.filter_by(username=session["usuario_logado"]).first()

    if request.method == "POST" and user.cargo == "ADM":
        titulo = request.form.get("titulo")
        descricao = request.form.get("descricao")
        prazo_str = request.form.get("prazo")
        atribuir_para = request.form.get("atribuir_para")

        prazo_data = datetime.strptime(prazo_str, "%Y-%m-%d").date()

        if atribuir_para == "TODOS":
            nova_tarefa = Tarefa(titulo=titulo, descricao=descricao, prazo=prazo_data, usuario_id=None)
            # Notificar todos os funcionarios
            todos_func = Usuario.query.filter(Usuario.cargo != "ADM").all()
            for f in todos_func:
                db.session.add(Notificacao(usuario_id=f.id, mensagem=f"Nova tarefa global: {titulo}"))
        else:
            nova_tarefa = Tarefa(titulo=titulo, descricao=descricao, prazo=prazo_data, usuario_id=int(atribuir_para))
            db.session.add(Notificacao(usuario_id=int(atribuir_para), mensagem=f"Nova tarefa atribuída a você: {titulo}"))

        db.session.add(nova_tarefa)
        db.session.commit()
        flash("Tarefa delegada com sucesso!", "success")
        return redirect(url_for("main.tasks"))

    if user.cargo == "ADM":
        lista_tarefas = Tarefa.query.order_by(Tarefa.id.desc()).all()
    else:
        lista_tarefas = Tarefa.query.filter(
            (Tarefa.usuario_id == user.id) | (Tarefa.usuario_id == None)
        ).order_by(Tarefa.id.desc()).all()

    return render_template("tasks.html", tarefas=lista_tarefas)


@bp.route("/tasks/concluir/<int:id>")
def concluir_tarefa(id):
    if "usuario_logado" not in session:
        return redirect(url_for("main.login"))

    user = Usuario.query.filter_by(username=session["usuario_logado"]).first()
    tarefa = db.session.get(Tarefa, id)
    
    if tarefa:
        if tarefa.usuario_id is None and user.cargo != "ADM":
            flash("Apenas um Administrador pode concluir uma tarefa global.", "error")
        else:
            tarefa.concluida = True
            
            if user.cargo != "ADM":
                flash(f"Tarefa '{tarefa.titulo}' concluída com sucesso. ADM notificado.", "success")
                db.session.add(Notificacao(usuario_id=None, mensagem=f"O funcionário {user.nome_exibicao} concluiu a tarefa: {tarefa.titulo}"))
            else:
                flash(f"Tarefa '{tarefa.titulo}' concluída.", "success")
                
            db.session.commit()

    return redirect(url_for("main.tasks"))


@bp.route("/tasks/reverter/<int:id>")
def reverter_tarefa(id):
    if "usuario_logado" not in session:
        return redirect(url_for("main.login"))

    user = Usuario.query.filter_by(username=session["usuario_logado"]).first()
    tarefa = db.session.get(Tarefa, id)
    
    if tarefa:
        if tarefa.usuario_id is None and user.cargo != "ADM":
            flash("Apenas um Administrador pode reverter uma tarefa global.", "error")
        elif tarefa.usuario_id != user.id and user.cargo != "ADM":
             flash("Você só pode reverter suas próprias tarefas.", "error")
        else:
            tarefa.concluida = False
            db.session.commit()
            flash(f"Status da tarefa '{tarefa.titulo}' foi revertido.", "info")

    return redirect(url_for("main.tasks"))

@bp.route("/tasks/remover/<int:id>")
def remover_tarefa(id):
    if "usuario_logado" not in session:
         return redirect(url_for("main.login"))
         
    user = Usuario.query.filter_by(username=session["usuario_logado"]).first()
    if user.cargo != 'ADM':
         return redirect(url_for("main.tasks"))

    tarefa = db.session.get(Tarefa, id)
    if tarefa:
        db.session.delete(tarefa)
        db.session.commit()
    return redirect(url_for("main.tasks"))


@bp.route("/reuniao", methods=["GET", "POST"])
def reuniao():
    if "usuario_logado" not in session:
        return redirect(url_for("main.login"))

    current_user = Usuario.query.filter_by(username=session["usuario_logado"]).first()

    if request.method == "POST" and current_user and current_user.cargo == "ADM":
        acao = request.form.get("acao")

        if acao == "criar_reuniao":
            nova_reuniao = Reuniao(
                titulo=request.form.get("titulo"),
                link=request.form.get("link"),  
                data=request.form.get("data"),
                horario=request.form.get("horario"),
                descricao=request.form.get("descricao")
            )
            db.session.add(nova_reuniao)
            db.session.commit()

        elif acao == "deletar_reuniao":
            reuniao_id = request.form.get("reuniao_id")
            reuniao_del = db.session.get(Reuniao, reuniao_id)
            if reuniao_del:
                db.session.delete(reuniao_del)
                db.session.commit()

        return redirect(url_for("main.reuniao"))

    reunioes = Reuniao.query.order_by(Reuniao.data.asc(), Reuniao.horario.asc()).all()

    hoje_data = date.today()
    ano = hoje_data.year
    mes = hoje_data.month
    hoje = hoje_data.day

    dia_semana_primeiro, dias_no_mes = calendar.monthrange(ano, mes)
    espacos_vazios = (dia_semana_primeiro + 1) % 7

    dias_com_reuniao = []
    for r in reunioes:
        if isinstance(r.data, date):
            if r.data.year == ano and r.data.month == mes:
                dias_com_reuniao.append(r.data.day)
        elif isinstance(r.data, str) and r.data:
            try:
                d_obj = date.fromisoformat(r.data)
                if d_obj.year == ano and d_obj.month == mes:
                    dias_com_reuniao.append(d_obj.day)
            except ValueError:
                pass

    eventos = Evento.query.all()

    return render_template(
        "reuniao.html",
        current_user=current_user,
        reunioes=reunioes,
        hoje=hoje,
        dias_no_mes=dias_no_mes,
        espacos_vazios=espacos_vazios,
        dias_com_reuniao=dias_com_reuniao,
        eventos=eventos
    )


@bp.route("/metas", methods=["GET", "POST"])
def metas():
    if "usuario_logado" not in session:
        return redirect(url_for("main.login"))

    current_user = Usuario.query.filter_by(username=session["usuario_logado"]).first()
    config_global = DashboardGlobal.query.first()

    if not config_global:
        config_global = DashboardGlobal()
        db.session.add(config_global)
        db.session.commit()

    # AÇÕES DO ADMINISTRADOR (POST)
    if request.method == "POST" and current_user and current_user.cargo == "ADM":
        action = request.form.get("action")

        # Atualizar Financeiro
        if action == "financeiro":
            config_global.faturamento = float(request.form.get("faturamento", 0))
            config_global.gastos = float(request.form.get("gastos", 0))
            db.session.commit()

        # Definir Funcionário do Mês
        elif action == "func_mes":
            usuario_id = request.form.get("usuario_id")
            justificativa = request.form.get("justificativa", "Destaque pelo excelente desempenho!")

            if usuario_id:
                user_selected = db.session.get(Usuario, int(usuario_id))
                if user_selected:
                    config_global.funcionario_mes = user_selected.nome_exibicao
                    novo_destaque = FuncionarioDoMes(usuario_id=user_selected.id, justificativa=justificativa)
                    db.session.add(novo_destaque)
                    db.session.commit()

        # Criar Evento
        elif action == "evento":
            titulo = request.form.get("titulo") or request.form.get("nome")
            data_ev = request.form.get("data")
            descricao_ev = request.form.get("descricao", "Evento institucional")

            if titulo and data_ev:
                novo_evento = Evento(
                    titulo=titulo,
                    data=data_ev,
                    descricao=descricao_ev
                )
                db.session.add(novo_evento)
                db.session.commit()

        # Deletar Evento
        elif action == "deletar_evento":
            evento_id = request.form.get("evento_id")
            ev_del = db.session.get(Evento, evento_id)
            if ev_del:
                db.session.delete(ev_del)
                db.session.commit()

        return redirect(url_for("main.metas"))

    # CÁLCULOS FINANCEIROS
    faturamento = config_global.faturamento or 0.0
    gastos = config_global.gastos or 0.0
    lucro = faturamento - gastos

    total = faturamento + gastos + abs(lucro)
    if total > 0:
        pct_faturamento = min((faturamento / total) * 100, 100)
        pct_gastos = min((gastos / total) * 100, 100)
        pct_lucro = min((max(0, lucro) / total) * 100, 100)
    else:
        pct_faturamento = pct_gastos = pct_lucro = 0

    # CONSULTAS PARA O TEMPLATE
    eventos = Evento.query.order_by(Evento.id.desc()).all()
    funcionario_destaque = FuncionarioDoMes.query.order_by(FuncionarioDoMes.id.desc()).first()
    todos_usuarios = Usuario.query.all()

    return render_template(
        "metas.html",
        current_user=current_user,
        config_global=config_global,
        lucro=lucro,
        pct_faturamento=pct_faturamento,
        pct_gastos=pct_gastos,
        pct_lucro=pct_lucro,
        todos_usuarios=todos_usuarios,
        eventos=eventos,
        funcionario_destaque=funcionario_destaque
    )


@bp.route("/funcionarios", methods=["GET", "POST"])
def funcionarios():
    if "usuario_logado" not in session:
        return redirect(url_for("main.login"))

    current_user = Usuario.query.filter_by(username=session["usuario_logado"]).first()

    if not current_user or current_user.cargo != "ADM":
        return redirect(url_for("main.home"))

    erro = None
    sucesso = None

    if request.method == "POST":
        acao = request.form.get("acao")

        if acao == "criar_funcionario":
            username = request.form.get("username", "").strip()
            senha = request.form.get("senha")
            nome_exibicao = request.form.get("nome_exibicao", "").strip()
            cargo = request.form.get("cargo", "FUNCIONARIO")

            if Usuario.query.filter_by(username=username).first():
                erro = "Este nome de usuário já está cadastrado!"
            else:
                novo_user = Usuario(
                    username=username,
                    senha_hash=generate_password_hash(senha),
                    nome_exibicao=nome_exibicao if nome_exibicao else username,
                    cargo=cargo
                )
                db.session.add(novo_user)
                db.session.commit()
                sucesso = f"Funcionário '@{username}' cadastrado com sucesso!"

        elif acao == "alterar_cargo":
            usuario_id = request.form.get("usuario_id")
            novo_cargo = request.form.get("novo_cargo")

            user_to_change = db.session.get(Usuario, usuario_id)
            if user_to_change:
                user_to_change.cargo = novo_cargo
                db.session.commit()
                sucesso = "Cargo atualizado com sucesso!"
                
        elif acao == "deletar_funcionario":
            usuario_id = request.form.get("usuario_id")
            user_to_delete = db.session.get(Usuario, usuario_id)
            
            if user_to_delete:
                if user_to_delete.id == current_user.id:
                    erro = "Você não pode deletar sua própria conta!"
                else:
                    Tarefa.query.filter_by(usuario_id=user_to_delete.id).delete()
                    Notificacao.query.filter_by(usuario_id=user_to_delete.id).delete()
                    FuncionarioDoMes.query.filter_by(usuario_id=user_to_delete.id).delete()
                    db.session.delete(user_to_delete)
                    db.session.commit()
                    sucesso = f"Funcionário {user_to_delete.username} deletado com sucesso!"

        elif acao == "resetar_senha":
            usuario_id = request.form.get("usuario_id")
            nova_senha = request.form.get("nova_senha")
            user_to_change = db.session.get(Usuario, usuario_id)
            if user_to_change and nova_senha:
                user_to_change.senha_hash = generate_password_hash(nova_senha)
                db.session.commit()
                sucesso = f"Senha de {user_to_change.username} redefinida!"


    todos_usuarios = Usuario.query.all()
    return render_template(
        "funcionarios.html",
        current_user=current_user,
        usuarios=todos_usuarios,
        erro=erro,
        sucesso=sucesso
    )
