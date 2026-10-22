import re
from datetime import date, timedelta

from app import create_app, db
from app.models import Insumo, Usuario


def cadastrar(client, **kw):
    dados = {
        "nome": "Ração Premium", "categoria": "racao", "lote": "L1",
        "quantidade": "10", "unidade": "kg",
        "validade": (date.today() + timedelta(days=60)).isoformat(),
        "doador": "Maria",
    }
    dados.update(kw)
    return client.post("/insumos/novo", data=dados)


# --- autenticacao -----------------------------------------------------------

def test_painel_exige_login(client):
    r = client.get("/")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_login_correto_e_incorreto(app, client):
    with app.app_context():
        u = Usuario(nome="Sandra", email="sandra@ong.org")
        u.set_senha("segredo123")
        db.session.add(u)
        db.session.commit()

    ruim = client.post("/login", data={"email": "sandra@ong.org", "senha": "x"})
    assert ruim.status_code == 200
    assert "E-mail ou senha incorretos" in ruim.get_data(as_text=True)

    bom = client.post("/login", data={"email": "SANDRA@ong.org", "senha": "segredo123"})
    assert bom.status_code == 302
    assert client.get("/").status_code == 200


def test_login_nao_redireciona_para_site_externo(app, client):
    with app.app_context():
        u = Usuario(nome="S", email="s@ong.org")
        u.set_senha("segredo123")
        db.session.add(u)
        db.session.commit()
    r = client.post("/login?next=https://evil.example",
                    data={"email": "s@ong.org", "senha": "segredo123"})
    assert r.headers["Location"] == "/"


def test_logout_encerra_sessao(logado):
    logado.post("/logout")
    assert logado.get("/").status_code == 302


# --- estoque ----------------------------------------------------------------

def test_cadastro_gera_comprovante_do_doador(app, logado):
    r = cadastrar(logado)
    assert r.status_code == 302
    page = logado.get(r.headers["Location"]).get_data(as_text=True)
    assert "Comprovante de doação" in page and "Maria" in page


def test_cadastro_invalido_e_recusado(app, logado):
    assert cadastrar(logado, quantidade="0").status_code == 400
    assert cadastrar(logado, categoria="brinquedo").status_code == 400
    assert cadastrar(logado, validade="31/12/2030").status_code == 400
    with app.app_context():
        assert Insumo.query.count() == 0


def test_baixa_rapida_usa_peps_e_atualiza_saldo(app, logado):
    cadastrar(logado, lote="LONGO", validade=(date.today() + timedelta(days=200)).isoformat())
    cadastrar(logado, lote="CURTO", validade=(date.today() + timedelta(days=15)).isoformat())

    logado.post("/baixa", data={"nome": "Ração Premium", "quantidade": "4"})

    with app.app_context():
        saldos = {i.lote: i.quantidade for i in Insumo.query.all()}
    assert saldos == {"CURTO": 6, "LONGO": 10}


def test_baixa_acima_do_saldo_mostra_erro_e_nao_altera(app, logado):
    cadastrar(logado, quantidade="3")
    r = logado.post("/baixa", data={"nome": "Ração Premium", "quantidade": "9"},
                    follow_redirects=True)
    assert "Saldo insuficiente" in r.get_data(as_text=True)
    with app.app_context():
        assert Insumo.query.one().quantidade == 3


def test_alerta_mostra_cor_icone_e_texto(app, logado):
    cadastrar(logado, validade=(date.today() + timedelta(days=3)).isoformat())
    html = logado.get("/alertas").get_data(as_text=True)
    assert "status-critico" in html and "⚠" in html and "Vence em até 7 dias" in html


def test_xss_e_escapado_no_painel(app, logado):
    cadastrar(logado, nome="<script>alert(1)</script>")
    html = logado.get("/").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


# --- seguranca --------------------------------------------------------------

def test_cabecalhos_de_seguranca(client):
    r = client.get("/login")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"


def test_post_sem_token_csrf_e_rejeitado():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    client = app.test_client()
    assert client.post("/login", data={"email": "a", "senha": "b"}).status_code == 400

    pagina = client.get("/login").get_data(as_text=True)
    token = re.search(r'name="_csrf" value="([0-9a-f]+)"', pagina).group(1)
    r = client.post("/login", data={"email": "a", "senha": "b", "_csrf": token})
    assert r.status_code == 200
