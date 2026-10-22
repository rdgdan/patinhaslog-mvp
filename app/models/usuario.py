from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class Usuario(db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(256), nullable=False)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha, method="pbkdf2:sha256")

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
