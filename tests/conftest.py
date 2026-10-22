import pytest

from app import create_app, db


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "teste",
            "CSRF_ENABLED": False,
        }
    )
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logado(app, client):
    """Client com sessao de um usuario autenticado."""
    from app.models import Usuario

    with app.app_context():
        u = Usuario(nome="Sandra", email="sandra@ong.org")
        u.set_senha("segredo123")
        db.session.add(u)
        db.session.commit()
    client.post("/login", data={"email": "sandra@ong.org", "senha": "segredo123"})
    return client
