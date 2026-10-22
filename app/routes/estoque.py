from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.models import Insumo
from app.models.insumo import CATEGORIAS
from app.security import login_required
from app.services.peps import baixar_por_peps, lotes_em_alerta, status_validade

bp = Blueprint("estoque", __name__)


@bp.route("/")
@login_required
def painel():
    insumos = Insumo.query.filter(Insumo.quantidade > 0).order_by(Insumo.validade).all()
    itens = [(i, status_validade(i)) for i in insumos]
    # Saldo utilizavel por produto: lotes vencidos nao entram na conta.
    produtos = {}
    for i, s in itens:
        p = produtos.setdefault(i.nome, {"saldo": 0, "unidade": i.unidade})
        if s != "vencido":
            p["saldo"] += i.quantidade
    return render_template("painel.html", itens=itens, produtos=sorted(produtos.items()))


@bp.route("/insumos/novo", methods=["GET", "POST"])
@login_required
def novo_insumo():
    if request.method == "POST":
        f = request.form
        try:
            insumo = Insumo(
                nome=f["nome"].strip(),
                categoria=f["categoria"],
                lote=f["lote"].strip(),
                quantidade=int(f["quantidade"]),
                unidade=f.get("unidade", "un").strip() or "un",
                validade=date.fromisoformat(f["validade"]),
                doador=f.get("doador", "").strip() or None,
            )
            if not insumo.nome or not insumo.lote:
                raise ValueError("Informe nome e lote.")
            if insumo.categoria not in CATEGORIAS:
                raise ValueError("Categoria inválida.")
            if insumo.quantidade <= 0:
                raise ValueError("A quantidade deve ser maior que zero.")
        except (KeyError, ValueError) as e:
            flash(f"Cadastro inválido: {e}", "danger")
            return render_template("insumo_form.html", categorias=CATEGORIAS), 400
        db.session.add(insumo)
        db.session.commit()
        flash("Insumo cadastrado.", "success")
        return redirect(url_for("estoque.comprovante", insumo_id=insumo.id))
    return render_template("insumo_form.html", categorias=CATEGORIAS)


@bp.route("/baixa", methods=["POST"])
@login_required
def baixa():
    nome = request.form.get("nome", "")
    try:
        retiradas = baixar_por_peps(nome, int(request.form.get("quantidade", "")))
    except ValueError as e:
        flash(str(e), "danger")
    else:
        detalhe = ", ".join(f"{q} do lote {l.lote}" for l, q in retiradas)
        flash(f"Baixa registrada: {detalhe}.", "success")
    return redirect(url_for("estoque.painel"))


@bp.route("/insumos/<int:insumo_id>/descartar", methods=["POST"])
@login_required
def descartar(insumo_id):
    insumo = db.get_or_404(Insumo, insumo_id)
    if status_validade(insumo) != "vencido":
        flash("Só é possível descartar lotes vencidos.", "danger")
    else:
        qtd = insumo.quantidade
        insumo.baixar(qtd)
        db.session.commit()
        flash(f"Lote {insumo.lote} descartado: {qtd} {insumo.unidade} de {insumo.nome}.", "success")
    return redirect(url_for("estoque.painel"))


@bp.route("/alertas")
@login_required
def alertas():
    return render_template("alertas.html", itens=lotes_em_alerta())


@bp.route("/comprovante/<int:insumo_id>")
@login_required
def comprovante(insumo_id):
    insumo = db.get_or_404(Insumo, insumo_id)
    return render_template("comprovante.html", insumo=insumo)
