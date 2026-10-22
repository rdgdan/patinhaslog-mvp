from app import _normalizar_db_url, create_app, db
from app.models import Usuario


def test_health_responde_ok_sem_login(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok", "banco": "ok"}


def test_health_retorna_503_quando_o_banco_falha(app, client, monkeypatch):
    def quebrado(*a, **kw):
        raise RuntimeError("banco fora")

    monkeypatch.setattr(db.session, "execute", quebrado)
    r = client.get("/health")
    assert r.status_code == 503
    assert r.get_json()["status"] == "erro"


def test_url_postgres_e_normalizada_para_o_sqlalchemy():
    assert _normalizar_db_url("postgres://u:p@h/db") == "postgresql://u:p@h/db"
    assert _normalizar_db_url("postgresql://u:p@h/db") == "postgresql://u:p@h/db"
    assert _normalizar_db_url("sqlite:///x.db") == "sqlite:///x.db"


def test_admin_inicial_e_criado_do_ambiente_uma_unica_vez(monkeypatch):
    monkeypatch.setenv("ADMIN_EMAIL", "Gestora@Ong.org")
    monkeypatch.setenv("ADMIN_PASSWORD", "segredo-de-teste")
    cfg = {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}
    app = create_app(cfg)
    with app.app_context():
        usuarios = Usuario.query.all()
        assert [u.email for u in usuarios] == ["gestora@ong.org"]
        assert usuarios[0].check_senha("segredo-de-teste")
        db.session.remove()
        db.drop_all()


def test_sem_variaveis_de_ambiente_nenhum_usuario_e_criado(app):
    with app.app_context():
        assert Usuario.query.count() == 0
