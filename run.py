import click

from app import create_app, db
from app.models import Usuario

app = create_app()


@app.cli.command("create-user")
@click.option("--nome", prompt=True)
@click.option("--email", prompt=True)
@click.password_option()
def create_user(nome, email, password):
    """Cria um usuario (gestora ou voluntario)."""
    u = Usuario(nome=nome, email=email.strip().lower())
    u.set_senha(password)
    db.session.add(u)
    db.session.commit()
    click.echo(f"Usuário {u.email} criado.")


if __name__ == "__main__":
    app.run(debug=False)
