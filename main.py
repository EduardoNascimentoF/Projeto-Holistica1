import os
# pyrefly: ignore [missing-import]
from flask import Flask
from models import db, Usuario, DashboardGlobal
from routes import bp as main_blueprint
# pyrefly: ignore [missing-import]
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

import os
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'usuarios.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(main_blueprint)

# INICIALIZANDO o DB
with app.app_context():
    db.create_all()
    if not DashboardGlobal.query.first():
        db.session.add(DashboardGlobal())
        db.session.commit()

if __name__ == "__main__":
    is_debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1']
    app.run(debug=is_debug)
