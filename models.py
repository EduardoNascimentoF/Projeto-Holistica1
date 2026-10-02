# pyrefly: ignore [missing-import]
from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

from datetime import datetime

class Notificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True) # None = ADM
    mensagem = db.Column(db.String(255), nullable=False)
    lida = db.Column(db.Boolean, default=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    cargo = db.Column(db.String(20), default="FUNCIONARIO")
    nome_exibicao = db.Column(db.String(100))
    foto_perfil = db.Column(db.String(300), default="https://i.pravatar.cc/150?img=11")
    bio = db.Column(db.Text, default="")

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
    link = db.Column(db.String(300))  
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
