from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.models import Usuario
from app.security import destino_seguro

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.check_senha(senha):
            session.clear()
            session["usuario_id"] = usuario.id
            session["usuario_nome"] = usuario.nome
            destino = request.args.get("next")
            return redirect(destino if destino_seguro(destino) else url_for("estoque.painel"))
        # Mensagem unica: nao revela se o e-mail existe.
        flash("E-mail ou senha incorretos.", "danger")
    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
