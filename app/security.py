"""Mitigacoes OWASP: CSRF, cabecalhos de seguranca, login obrigatorio e redirect seguro."""

import hmac
import secrets
from functools import wraps
from urllib.parse import urlparse

from flask import abort, current_app, redirect, request, session, url_for


def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(16)
    return session["_csrf"]


def init_security(app):
    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def verificar_csrf():
        if not current_app.config.get("CSRF_ENABLED", True):
            return
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            enviado = request.form.get("_csrf", "")
            esperado = session.get("_csrf", "")
            if not esperado or not hmac.compare_digest(enviado, esperado):
                abort(400, "Token CSRF inválido.")

    @app.after_request
    def cabecalhos(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "same-origin"
        return resp


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def destino_seguro(destino):
    """Aceita so caminhos internos, evitando open redirect."""
    if not destino:
        return False
    p = urlparse(destino)
    return not p.scheme and not p.netloc and destino.startswith("/") and not destino.startswith("//")
