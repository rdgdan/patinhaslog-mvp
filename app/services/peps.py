"""Regra PEPS (primeiro que entra, primeiro que sai) com foco no vencimento.

Os lotes com validade mais proxima sao consumidos primeiro, o que reduz o
desperdicio de insumos vencidos (ODS 12, meta 12.5).
"""

from datetime import date, timedelta

from app import db
from app.models import Insumo

DIAS_CRITICO = 7
DIAS_ATENCAO = 30


def status_validade(insumo, hoje=None):
    """Classifica o lote como vencido, critico, atencao ou ok."""
    hoje = hoje or date.today()
    if insumo.validade < hoje:
        return "vencido"
    if insumo.validade <= hoje + timedelta(days=DIAS_CRITICO):
        return "critico"
    if insumo.validade <= hoje + timedelta(days=DIAS_ATENCAO):
        return "atencao"
    return "ok"


def lotes_em_alerta(hoje=None):
    """Lotes com saldo que estao vencidos ou perto de vencer, mais urgentes primeiro."""
    lotes = (
        Insumo.query.filter(Insumo.quantidade > 0).order_by(Insumo.validade).all()
    )
    classificados = [(l, status_validade(l, hoje)) for l in lotes]
    return [(l, s) for l, s in classificados if s != "ok"]


def baixar_por_peps(nome, quantidade, hoje=None):
    """Baixa `quantidade` do produto `nome`, consumindo primeiro os lotes que vencem antes.

    Lotes ja vencidos nao sao consumidos. Se o saldo utilizavel nao cobrir o
    pedido, nada e alterado e ValueError e levantado.
    Retorna a lista de (lote, quantidade_retirada).
    """
    if quantidade <= 0:
        raise ValueError("A quantidade da baixa deve ser maior que zero.")

    hoje = hoje or date.today()
    lotes = (
        Insumo.query.filter(
            Insumo.nome == nome,
            Insumo.quantidade > 0,
            Insumo.validade >= hoje,
        )
        .order_by(Insumo.validade, Insumo.data_entrada, Insumo.id)
        .all()
    )

    disponivel = sum(l.quantidade for l in lotes)
    if quantidade > disponivel:
        raise ValueError(
            f"Saldo insuficiente de {nome}: há {disponivel} dentro da validade, "
            f"pedido {quantidade}."
        )

    retiradas = []
    restante = quantidade
    for lote in lotes:
        if restante == 0:
            break
        retirar = min(lote.quantidade, restante)
        lote.baixar(retirar)
        retiradas.append((lote, retirar))
        restante -= retirar

    db.session.commit()
    return retiradas
