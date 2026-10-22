from datetime import date, timedelta

import pytest

from app import db
from app.models import Insumo
from app.services.peps import baixar_por_peps, lotes_em_alerta, status_validade

HOJE = date(2026, 6, 1)


def lote(nome="Ração Premium", lote="L", qtd=10, dias=100, entrada=None):
    return Insumo(
        nome=nome,
        categoria="racao",
        lote=lote,
        quantidade=qtd,
        unidade="kg",
        validade=HOJE + timedelta(days=dias),
        data_entrada=entrada or HOJE,
    )


@pytest.mark.parametrize(
    "dias,esperado",
    [(-1, "vencido"), (0, "critico"), (7, "critico"), (8, "atencao"),
     (30, "atencao"), (31, "ok")],
)
def test_status_validade(dias, esperado):
    assert status_validade(lote(dias=dias), HOJE) == esperado


def test_baixa_consome_primeiro_o_lote_que_vence_antes(app):
    with app.app_context():
        db.session.add_all([lote(lote="LONGO", qtd=10, dias=200),
                            lote(lote="CURTO", qtd=10, dias=20)])
        db.session.commit()

        retiradas = baixar_por_peps("Ração Premium", 4, HOJE)

        assert [(l.lote, q) for l, q in retiradas] == [("CURTO", 4)]
        saldos = {l.lote: l.quantidade for l in Insumo.query.all()}
        assert saldos == {"CURTO": 6, "LONGO": 10}


def test_baixa_atravessa_varios_lotes(app):
    with app.app_context():
        db.session.add_all([lote(lote="A", qtd=3, dias=10),
                            lote(lote="B", qtd=5, dias=50)])
        db.session.commit()

        retiradas = baixar_por_peps("Ração Premium", 6, HOJE)

        assert [(l.lote, q) for l, q in retiradas] == [("A", 3), ("B", 3)]


def test_baixa_ignora_lote_vencido(app):
    with app.app_context():
        db.session.add_all([lote(lote="VENCIDO", qtd=10, dias=-5),
                            lote(lote="OK", qtd=2, dias=40)])
        db.session.commit()

        with pytest.raises(ValueError):
            baixar_por_peps("Ração Premium", 3, HOJE)

        assert Insumo.query.filter_by(lote="VENCIDO").one().quantidade == 10


def test_baixa_insuficiente_nao_altera_nada(app):
    with app.app_context():
        db.session.add_all([lote(lote="A", qtd=3, dias=10),
                            lote(lote="B", qtd=2, dias=50)])
        db.session.commit()

        with pytest.raises(ValueError):
            baixar_por_peps("Ração Premium", 6, HOJE)

        assert {l.lote: l.quantidade for l in Insumo.query.all()} == {"A": 3, "B": 2}


def test_alertas_ordenados_por_urgencia_e_sem_lotes_zerados(app):
    with app.app_context():
        db.session.add_all([
            lote(lote="OK", dias=90),
            lote(lote="ATENCAO", dias=20),
            lote(lote="VENCIDO", dias=-2),
            lote(lote="ZERADO", qtd=0, dias=3),
        ])
        db.session.commit()

        resultado = [(l.lote, s) for l, s in lotes_em_alerta(HOJE)]

        assert resultado == [("VENCIDO", "vencido"), ("ATENCAO", "atencao")]
