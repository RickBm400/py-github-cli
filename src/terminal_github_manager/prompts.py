import typer

from . import config

TOKEN_HELP = "Token personal de GitHub. Se requiere el scope 'repo' paraadministration y repos privados."


def ask_token() -> str | None:
    if not config.is_interactive():
        return None
    token = typer.prompt(
        "No se encontro GH_TOKEN. Ingresa tu token personal de GitHub",
        hide_input=True,
        default="",
        show_default=False,
    ).strip()
    return token or None