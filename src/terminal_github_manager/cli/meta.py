import typer

from .. import banner, config, output, prompts
from ..exceptions import GitHubManagerError
from ..version import get_version


def root_callback(
    ctx: typer.Context,
    show_version: bool = typer.Option(False, "--version", "-V", help="Muestra la version y termina."),
) -> None:
    if show_version:
        output.raw(banner.render_version())
        ctx.exit(0)
    if ctx.invoked_subcommand is None:
        output.raw(banner.render_banner())
        ctx.get_help()
        ctx.exit(0)


def banner_command() -> None:
    """Muestra el mensaje de bienvenida con la version."""
    output.raw(banner.render_banner())


def version_command() -> None:
    """Muestra la version instalada."""
    output.detail(banner.render_version())


def login_command() -> None:
    """Guarda un token de GitHub en la configuracion del usuario."""
    token = prompts.ask_token()
    if not token:
        output.error(
            GitHubManagerError(
                "no se ingreso ningun token",
                hint="ejecuta 'ghm login' en una terminal interactiva o define GH_TOKEN en el entorno",
            )
        )
        raise typer.Exit(code=1)

    path = config.save_token(token)
    output.info(f"Token guardado en {path}")
    output.info("Ese archivo tiene permisos 600: no lo compartas ni lo versiones.")


def config_command() -> None:
    """Muestra la ruta de configuracion y si existe un token guardado."""
    source = config.token_source()
    output.field_table(
        "Configuracion",
        [
            ("Version", get_version()),
            ("Archivo de configuracion", str(config.config_path())),
            ("Directorio", str(config.config_dir())),
            ("Token detectado", "si" if source else "no"),
            ("Origen del token", source),
        ],
    )