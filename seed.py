from main import app, db
from models import Usuario
from werkzeug.security import generate_password_hash

def seed_users():
    with app.app_context():
        if not Usuario.query.first():
            print("Criando usuários iniciais...")
            admin = Usuario(
                username="Eduardo",
                senha_hash=generate_password_hash("123"),
                cargo="ADM",
                nome_exibicao="Eduardo (Diretor)"
            )
            funcionario = Usuario(
                username="jose.geth",
                senha_hash=generate_password_hash("123"),
                cargo="FUNCIONARIO",
                nome_exibicao="José Geth"
            )
            db.session.add(admin)
            db.session.add(funcionario)
            db.session.commit()
            print("Usuários criados com sucesso!")
        else:
            print("Os usuários já existem no banco de dados.")

if __name__ == '__main__':
    seed_users()
