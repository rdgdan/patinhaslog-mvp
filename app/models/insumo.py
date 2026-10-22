from datetime import date

from app import db

CATEGORIAS = ("racao", "medicamento")


class Insumo(db.Model):
    """Um lote de insumo doado (ração ou medicamento veterinário)."""

    __tablename__ = "insumo"
    __table_args__ = (
        db.CheckConstraint("quantidade >= 0", name="ck_insumo_saldo_nao_negativo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False, index=True)
    categoria = db.Column(db.String(20), nullable=False)
    lote = db.Column(db.String(50), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    unidade = db.Column(db.String(10), nullable=False, default="un")
    validade = db.Column(db.Date, nullable=False)
    doador = db.Column(db.String(120))
    data_entrada = db.Column(db.Date, nullable=False, default=date.today)

    def baixar(self, qtd):
        """Retira `qtd` do saldo. O saldo nunca fica negativo."""
        if qtd <= 0:
            raise ValueError("A quantidade da baixa deve ser maior que zero.")
        if qtd > self.quantidade:
            raise ValueError(
                f"Saldo insuficiente no lote {self.lote}: "
                f"há {self.quantidade}, pedido {qtd}."
            )
        self.quantidade -= qtd
