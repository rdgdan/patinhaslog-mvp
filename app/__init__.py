import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def _normalizar_db_url(url):
    """Aponta URLs de Postgres para o driver psycopg2 instalado.

    As hospedagens entregam postgres://, e o SQLAlchemy 2.1 assume o psycopg 3
    quando o driver nao e informado.
    """
    for prefixo in ("postgres://", "postgresql://"):
        if url.startswith(prefixo):
            return "postgresql+psycopg2://" + url[len(prefixo):]
    return url


def _criar_admin_inicial():
    """Cria o primeiro usuario a partir do ambiente, util onde nao ha terminal."""
    from app.models import Usuario

    email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
    senha = os.environ.get("ADMIN_PASSWORD", "")
    if not email or not senha or Usuario.query.first():
        return
    usuario = Usuario(nome=os.environ.get("ADMIN_NOME", "Gestora"), email=email)
    usuario.set_senha(senha)
    db.session.add(usuario)
    db.session.commit()


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-troque-em-producao"),
        SQLALCHEMY_DATABASE_URI=_normalizar_db_url(
            os.environ.get("DATABASE_URL", "sqlite:///patinhaslog.db")
        ),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE") == "1",
    )
    if config:
        app.config.update(config)

    db.init_app(app)

    from app import models  # noqa: F401  (registra as tabelas)

    from app.demo import criar_usuario_demo, popular_estoque_demo
    from app.routes import auth, estoque, health
    from app.security import init_security

    init_security(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(estoque.bp)
    app.register_blueprint(health.bp)

    with app.app_context():
        db.create_all()
        _criar_admin_inicial()
        criar_usuario_demo()
        popular_estoque_demo()

    return app
