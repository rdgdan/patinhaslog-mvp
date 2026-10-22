import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-troque-em-producao"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL", "sqlite:///patinhaslog.db"
        ),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if config:
        app.config.update(config)

    db.init_app(app)

    from app import models  # noqa: F401  (registra as tabelas)

    from app.routes import auth, estoque
    from app.security import init_security

    init_security(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(estoque.bp)

    with app.app_context():
        db.create_all()

    return app
