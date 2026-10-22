# PatinhasLog

Controle de estoque para a **ONG Patinhas do Bem**, gerida por Sandra Maria.
Rações e medicamentos veterinários doados costumam vencer antes de serem usados.
O PatinhasLog aplica o método **PEPS** (primeiro que entra, primeiro que sai) e avisa
quais lotes estão perto do vencimento.

**ODS 12 — Consumo e Produção Responsáveis, Meta 12.5:** reduzir substancialmente a geração de resíduos.

## Stack

Python 3.12 · Flask · Flask-SQLAlchemy · Werkzeug · Bootstrap 5 · SQLite (dev) / PostgreSQL (produção)

## Estrutura

```
app/
  __init__.py     # application factory
  models/         # Usuario, Insumo
  routes/         # auth, estoque
  services/       # regra PEPS
  templates/      # Jinja2 + Bootstrap 5
tests/            # pytest (unitários e integração)
.github/workflows/ci.yml
```

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python run.py
```

Crie o primeiro usuário com `flask --app run create-user`.

## Testes

```bash
pytest
```

## Convenção de commits

Commits semânticos: `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `ci:`.
Todo trabalho entra por branch e Pull Request, com auto-revisão técnica antes do merge.
