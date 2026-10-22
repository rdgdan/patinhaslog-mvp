"""Usuario e dados de demonstracao, ativados so por variaveis de ambiente."""

import os
from datetime import date, timedelta

from app import db
from app.models import Insumo, Usuario

# (nome, categoria, lote, quantidade, unidade, dias para vencer, doador)
LOTES_DEMO = [
    ("Ração Premium Cães", "racao", "RC-0825", 18, "kg", -3, "Pet Mais"),
    ("Vermífugo Canino", "medicamento", "VM-114", 12, "cx", 4, "Clínica Vida Animal"),
    ("Ração Premium Cães", "racao", "RC-1026", 25, "kg", 21, "Maria Souza"),
    ("Antipulgas 10kg", "medicamento", "AP-077", 8, "un", 26, "João Lima"),
    ("Ração Filhotes", "racao", "RF-0127", 40, "kg", 90, "Pet Mais"),
    ("Ração Gatos Adultos", "racao", "RG-0227", 30, "kg", 150, "Mercado Bom Preço"),
]


def criar_usuario_demo():
    """Cria o usuario de demonstracao se DEMO_EMAIL e DEMO_PASSWORD existirem."""
    email = os.environ.get("DEMO_EMAIL", "").strip().lower()
    senha = os.environ.get("DEMO_PASSWORD", "")
    if not email or not senha or Usuario.query.filter_by(email=email).first():
        return
    usuario = Usuario(nome="Usuário de demonstração", email=email)
    usuario.set_senha(senha)
    db.session.add(usuario)
    db.session.commit()


def popular_estoque_demo():
    """Com DEMO_SEED=1 e estoque vazio, cadastra lotes de exemplo."""
    if os.environ.get("DEMO_SEED") != "1" or Insumo.query.first():
        return
    hoje = date.today()
    for nome, cat, lote, qtd, un, dias, doador in LOTES_DEMO:
        db.session.add(Insumo(nome=nome, categoria=cat, lote=lote, quantidade=qtd,
                              unidade=un, validade=hoje + timedelta(days=dias),
                              doador=doador))
    db.session.commit()
