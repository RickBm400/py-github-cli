import json as json_module

from rich.console import Console
from rich.table import Table

from .exceptions import GitHubManagerError

console = Console()
error_console = Console(stderr=True)


def json(payload: object) -> None:
    console.print_json(json_module.dumps(payload))


def raw(text: str) -> None:
    console.print(text, markup=False, highlight=False, crop=False, soft_wrap=True)


def field_table(title: str, rows: list[tuple[str, object]]) -> None:
    table = Table(title=title, show_header=False, title_justify="left")
    table.add_column("Campo", style="bold cyan")
    table.add_column("Valor")
    for key, value in rows:
        table.add_row(key, "-" if value is None else str(value))
    console.print(table)


def repository_table(repositories: list) -> None:
    table = Table(title=f"Repositorios ({len(repositories)})")
    table.add_column("Nombre")
    table.add_column("Visibilidad")
    table.add_column("Archivado")
    table.add_column("Lenguaje")
    table.add_column("Topics")
    table.add_column("Actualizado")
    table.add_column("URL")
    for repo in repositories:
        table.add_row(
            repo.full_name,
            repo.visibility,
            "si" if repo.archived else "no",
            repo.language or "-",
            ", ".join(repo.topics) or "-",
            str(repo.updated_at),
            repo.html_url,
        )
    console.print(table)


def repository_details(snapshot: dict) -> list[tuple[str, object]]:
    return [
        ("Nombre", snapshot["full_name"]),
        ("Descripcion", snapshot["description"]),
        ("Pagina principal", snapshot["homepage"]),
        ("Visibilidad", snapshot["visibility"]),
        ("Archivado", "si" if snapshot["archived"] else "no"),
        ("Propietario", snapshot["owner"]),
        ("Lenguaje", snapshot["language"]),
        ("Topics", ", ".join(snapshot["topics"]) or None),
        ("Rama por defecto", snapshot["default_branch"]),
        ("Issues", snapshot["has_issues"]),
        ("Wiki", snapshot["has_wiki"]),
        ("Proyectos", snapshot["has_projects"]),
        ("Discusiones", snapshot["has_discussions"]),
        ("Descargas", snapshot["has_downloads"]),
        ("Licencia", snapshot["license"]),
        ("Creado", snapshot["created_at"]),
        ("Actualizado", snapshot["updated_at"]),
        ("Ultimo push (actividad)", snapshot["pushed_at"]),
        ("Tamano (KB)", snapshot["size_kb"]),
        ("Estrellas", snapshot["stars"]),
        ("Forks", snapshot["forks"]),
        ("Observadores", snapshot["watchers"]),
        ("Issues abiertos", snapshot["open_issues"]),
        ("URL", snapshot["url"]),
        ("Clone (HTTPS)", snapshot["clone_url"]),
        ("Clone (SSH)", snapshot["ssh_url"]),
    ]


def license_details(data: dict) -> list[tuple[str, object]]:
    license_info = data["license"]
    return [
        ("Repositorio", data["full_name"]),
        ("Descripcion", data["description"]),
        ("Visibilidad", data["visibility"]),
        ("Archivado", "si" if data["archived"] else "no"),
        ("Lenguaje", data["language"]),
        ("Rama por defecto", data["default_branch"]),
        ("Licencia (nombre)", license_info["name"]),
        ("Licencia (spdx_id)", license_info["spdx_id"]),
        ("Licencia (key)", license_info["key"]),
        ("Archivo de licencia", license_info["file"]),
        ("SHA", license_info["sha"]),
        ("Tamano (bytes)", license_info["size"]),
        ("Creado", data["created_at"]),
        ("Actualizado", data["updated_at"]),
        ("Ultimo push (actividad)", data["pushed_at"]),
        ("Tamano del repo (KB)", data["size_kb"]),
        ("Estrellas", data["stars"]),
        ("Forks", data["forks"]),
        ("Issues abiertos", data["open_issues"]),
        ("URL licencia", license_info["url"]),
        ("URL archivo", license_info["html_url"]),
    ]


def info(message: str) -> None:
    console.print(message)


def detail(message: str) -> None:
    console.print(message)


def cancelled(message: str) -> None:
    error_console.print(f"[yellow]Cancelado:[/yellow] {message}")


def notice(message: str) -> None:
    error_console.print(f"[yellow]Aviso:[/yellow] {message}")


def error(error_data: GitHubManagerError) -> None:
    error_console.print(f"[red]Error:[/red] {error_data.message}")
    if error_data.hint:
        error_console.print(f"[yellow]Ayuda:[/yellow] {error_data.hint}")
    for line in error_data.details:
        error_console.print(f"  [dim]-[/dim] {line}")
    if error_data.documentation:
        error_console.print(f"[dim]Documentacion: {error_data.documentation}[/dim]")