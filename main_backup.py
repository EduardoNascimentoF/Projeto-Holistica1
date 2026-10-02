import os
import calendar
# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request, redirect, url_for, session
# pyrefly: ignore [missing-import]
from flask_sqlalchemy import SQLAlchemy
# pyrefly: ignore [missing-import]
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'senha_secreta_q_vou_mudar_dps'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# MODELO DO BANCO DE DADOS

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    cargo = db.Column(db.String(20), default="FUNCIONARIO")
    nome_exibicao = db.Column(db.String(100))
    foto_perfil = db.Column(db.String(300), default="https://i.pravatar.cc/150?img=11")

    @property
    def tarefas_concluidas_count(self):
        return len([t for t in self.tarefas if t.concluida])

    @property
    def tarefas_falhadas_count(self):
        return len([t for t in self.tarefas if not t.concluida and t.prazo < date.today()])


class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    prazo = db.Column(db.Date, nullable=False)
    concluida = db.Column(db.Boolean, default=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    usuario = db.relationship('Usuario', backref=db.backref('tarefas', lazy=True))

    @property
    def passou_do_prazo(self):
        return not self.concluida and self.prazo < date.today()


class Reuniao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(300))  # <--- CORRIGIDO: Adicionada a coluna de link
    data = db.Column(db.String(20), nullable=False)
    horario = db.Column(db.String(20))
    descricao = db.Column(db.Text)


class FuncionarioDoMes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    justificativa = db.Column(db.Text, nullable=False)
    usuario = db.relationship('Usuario', backref='destaques')


class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    data = db.Column(db.String(20), nullable=False)
    descricao = db.Column(db.Text, nullable=False)


class DashboardGlobal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    faturamento = db.Column(db.Float, default=50000.0)
    gastos = db.Column(db.Float, default=20000.0)
    funcionario_mes = db.Column(db.String(100), default="Nenhum")


# Injetor global
@app.context_processor
def inject_user_data():
    if "usuario_logado" in session:
        user = Usuario.query.filter_by(username=session["usuario_logado"]).first()
        todos_usuarios = Usuario.query.filter(Usuario.cargo != "ADM").all()
        return dict(current_user=user, todos_usuarios=todos_usuarios)
    return dict(current_user=None, todos_usuarios=[])


# INICIALIZANDO o DB
with app.app_context():
    db.create_all()
    if not DashboardGlobal.query.first():
        db.session.add(DashboardGlobal())
    if not Usuario.query.first():
        db.session.add(Usuario(username="Eduardo", senha_hash=generate_password_hash("123"), cargo="ADM",
                               nome_exibicao="Eduardo (Diretor)"))
        db.session.add(Usuario(username="jose.geth", senha_hash=generate_password_hash("123"), cargo="FUNCIONARIO",
                               nome_exibicao="José Geth"))
        db.session.commit()


# ROTAS DO SISTEMA

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario_digitado = request.form.get("username")
        senha_digitada = request.form.get("password")
        user = Usuario.query.filter_by(username=usuario_digitado).first()

        if user and check_password_hash(user.senha_hash, senha_digitada):
            session["usuario_logado"] = user.username
            session["cargo_usuario"] = user.cargo
            return redirect(url_for("home"))
        return render_template("index.html", erro="Usuário ou senha incorretos!")
    return render_template("index.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        usuario_digitado = request.form.get("username")
        senha_digitada = request.form.get("password")
        if Usuario.query.filter_by(username=usuario_digitado).first():
            return render_template("registro.html", erro="Usuário já cadastrado!")

        novo_user = Usuario(username=usuario_digitado, senha_hash=generate_password_hash(senha_digitada),
                            nome_exibicao=usuario_digitado)
        db.session.add(novo_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("registro.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/home")
def home():
    if "usuario_logado" not in session: return redirect(url_for("login"))
    return render_template("home.html")


@app.route("/perfil/atualizar", methods=["POST"])
def atualizar_perfil():
    if "usuario_logado" not in session: return redirect(url_for("login"))
    user = Usuario.query.filter_by(username=session["usuario_logado"]).first()

    novo_nome = request.form.get("nome_exibicao")
    nova_foto = request.form.get("foto_perfil")

    if novo_nome: user.nome_exibicao = novo_nome
    if nova_foto: user.foto_perfil = nova_foto
    db.session.commit()
    return redirect(request.referrer or url_for("home"))


@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    if "usuario_logado" not in session: return redirect(url_for("login"))
    user = Usuario.query.filter_by(username=session["usuario_logado"]).first()

    if request.method == "POST" and user.cargo == "ADM":
        titulo = request.form.get("titulo")
        descricao = request.form.get("descricao")
        prazo_str = request.form.get("prazo")
        atribuir_para = request.form.get("atribuir_para")

        prazo_data = datetime.strptime(prazo_str, "%Y-%m-%d").date()

        if atribuir_para == "TODOS":
            nova_tarefa = Tarefa(titulo=titulo, descricao=descricao, prazo=prazo_data, usuario_id=None)
        else:
            nova_tarefa = Tarefa(titulo=titulo, descricao=descricao, prazo=prazo_data, usuario_id=int(atribuir_para))

        db.session.add(nova_tarefa)
        db.session.commit()
        return redirect(url_for("tasks"))

    if user.cargo == "ADM":
        lista_tarefas = Tarefa.query.all()
    else:
        lista_tarefas = Tarefa.query.filter((Tarefa.usuario_id == user.id) | (Tarefa.usuario_id == None)).all()

    return render_template("tasks.html", tarefas=lista_tarefas)


@app.route("/tasks/concluir/<int:id>")
def concluir_tarefa(id):
    if "usuario_logado" not in session: return redirect(url_for("login"))
    tarefa = db.session.get(Tarefa, id)
    if tarefa:
        tarefa.concluida = True
        db.session.commit()
    return redirect(url_for("tasks"))


@app.route("/tasks/remover/<int:id>")
def remover_tarefa(id):
    tarefa = db.session.get(Tarefa, id)
    if tarefa:
        db.session.delete(tarefa)
        db.session.commit()
    return redirect(url_for("tasks"))


@app.route("/reuniao", methods=["GET", "POST"])
def reuniao():
    if "usuario_logado" not in session:
        return redirect(url_for("login"))

    current_user = Usuario.query.filter_by(username=session["usuario_logado"]).first()

    if request.method == "POST" and current_user and current_user.cargo == "ADM":
        acao = request.form.get("acao")

        if acao == "criar_reuniao":
            nova_reuniao = Reuniao(
                titulo=request.form.get("titulo"),
                link=request.form.get("link"),  # <--- CORRIGIDO: Capturando o campo link do formulário
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

        return redirect(url_for("reuniao"))

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


@app.route("/metas", methods=["GET", "POST"])
def metas():
    if "usuario_logado" not in session:
        return redirect(url_for("login"))

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

        # 4. Deletar Evento
        elif action == "deletar_evento":
            evento_id = request.form.get("evento_id")
            ev_del = db.session.get(Evento, evento_id)
            if ev_del:
                db.session.delete(ev_del)
                db.session.commit()

        return redirect(url_for("metas"))

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
@app.route("/funcionarios", methods=["GET", "POST"])
def funcionarios():
    if "usuario_logado" not in session:
        return redirect(url_for("login"))

    current_user = Usuario.query.filter_by(username=session["usuario_logado"]).first()

    if not current_user or current_user.cargo != "ADM":
        return redirect(url_for("home"))

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

    todos_usuarios = Usuario.query.all()
    return render_template(
        "funcionarios.html",
        current_user=current_user,
        usuarios=todos_usuarios,
        erro=erro,
        sucesso=sucesso
    )


if __name__ == "__main__":
    app.run(debug=True)