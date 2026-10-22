import typer

from .cli import meta, repos

app = typer.Typer(
    name="ghm",
    help="gestion de repositorios de GitHub desde la terminal.",
    invoke_without_command=True,
    callback=meta.root_callback,
)
app.add_typer(repos.app)
app.command("banner", help="Muestra el mensaje de bienvenida con la version.")(meta.banner_command)
app.command("version", help="Muestra la version instalada.")(meta.version_command)
app.command("login", help="Guarda un token de GitHub en la configuracion del usuario.")(meta.login_command)
app.command("config", help="Muestra la ruta de configuracion y el origen del token.")(meta.config_command)


def main():
    app()


if __name__ == "__main__":
    main()