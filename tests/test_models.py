from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Insumo, Usuario


def novo_insumo(**kw):
    dados = dict(
        nome="Ração Premium",
        categoria="racao",
        lote="L1",
        quantidade=10,
        unidade="kg",
        validade=date(2030, 1, 1),
    )
    dados.update(kw)
    return Insumo(**dados)


def test_senha_nunca_e_guardada_em_texto_puro():
    u = Usuario(nome="Sandra", email="sandra@ong.org")
    u.set_senha("segredo123")
    assert u.senha_hash != "segredo123"
    assert u.senha_hash.startswith("pbkdf2:sha256")
    assert u.check_senha("segredo123")
    assert not u.check_senha("errada")


def test_email_do_usuario_e_unico(app):
    with app.app_context():
        for _ in range(2):
            u = Usuario(nome="A", email="a@ong.org")
            u.set_senha("x")
            db.session.add(u)
        with pytest.raises(IntegrityError):
            db.session.commit()


def test_baixa_reduz_saldo():
    i = novo_insumo(quantidade=10)
    i.baixar(4)
    assert i.quantidade == 6


def test_baixa_acima_do_saldo_e_recusada():
    i = novo_insumo(quantidade=3)
    with pytest.raises(ValueError):
        i.baixar(4)
    assert i.quantidade == 3


@pytest.mark.parametrize("qtd", [0, -1])
def test_baixa_nao_positiva_e_recusada(qtd):
    with pytest.raises(ValueError):
        novo_insumo().baixar(qtd)


def test_banco_recusa_saldo_negativo(app):
    with app.app_context():
        db.session.add(novo_insumo(quantidade=-1))
        with pytest.raises(IntegrityError):
            db.session.commit()
