from flask import Blueprint, jsonify
from sqlalchemy import text

from app import db

bp = Blueprint("health", __name__)


@bp.route("/health")
def health():
    """Verificacao de disponibilidade para o monitoramento (sem login)."""
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:
        return jsonify(status="erro", banco="indisponivel"), 503
    return jsonify(status="ok", banco="ok")
