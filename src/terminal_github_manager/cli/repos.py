import typer

from .. import output
from ..services import repository_service as repos
from ..services.github_session import github_session
from .options import enum_value, handle_errors, split_topics

app = typer.Typer(
    name="repo",
    help="Gestion de repositorios: listar, consultar, crear, editar, archivar, eliminar, clonar y abrir.",
    no_args_is_help=True,
)

VISIBILITY_CHOICES = ("public", "private")
VISIBILITY_FILTER_CHOICES = ("all", "public", "private")
AFFILIATION_CHOICES = ("owner", "collaborator", "organization_member", "member")
SORT_CHOICES = ("created", "updated", "pushed", "full_name")
DIRECTION_CHOICES = ("asc", "desc")


@app.command("list")
@handle_errors
def list_repos(
    affiliation: str = typer.Option(
        "owner", "--affiliation", help="owner, collaborator, organization_member o member."
    ),
    visibility: str | None = typer.Option(None, "--visibility", help="public, private o all."),
    archived: bool | None = typer.Option(
        None, "--archived/--not-archived", help="Filtra por estado de archivado."
    ),
    sort: str = typer.Option("updated", "--sort", help="created, updated, pushed o full_name."),
    direction: str = typer.Option("desc", "--direction", help="asc o desc."),
    limit: int = typer.Option(0, "--limit", "-n", help="Maximo de repositorios (0 = todos)."),
    as_json: bool = typer.Option(False, "--json", help="Muestra la salida en JSON."),
):
    """Lista repositorios del usuario autenticado: publicos, privados y archivados."""
    enum_value("affiliation", affiliation, AFFILIATION_CHOICES)
    enum_value("visibility", visibility, VISIBILITY_FILTER_CHOICES)
    enum_value("sort", sort, SORT_CHOICES)
    enum_value("direction", direction, DIRECTION_CHOICES)

    with github_session() as session:
        repositories = repos.list_repositories(
            session,
            affiliation=affiliation,
            visibility=visibility,
            sort=sort,
            direction=direction,
            archived=archived,
            limit=limit,
        )

    if as_json:
        output.json([repos.repository_snapshot(repo) for repo in repositories])
        return
    output.repository_table(repositories)


@app.command("view")
@handle_errors
def view_repo(
    reference: str = typer.Argument(..., help="Nombre del repositorio del usuario autenticado."),
    as_json: bool = typer.Option(False, "--json", help="Muestra la salida en JSON."),
):
    """Muestra detalles, fecha de creacion, ultima actualizacion, tamano y actividad."""
    with github_session() as session:
        repo = repos.resolve_repository(session, reference)
        snapshot = repos.repository_snapshot(repo)

    if as_json:
        output.json(snapshot)
        return
    output.field_table(snapshot["full_name"], output.repository_details(snapshot))


@app.command("create")
@handle_errors
def create_repo(
    name: str = typer.Argument(..., help="Nombre del nuevo repositorio."),
    description: str | None = typer.Option(None, "--description", "-d", help="Descripcion inicial."),
    homepage: str | None = typer.Option(None, "--homepage", help="Pagina principal inicial."),
    visibility: str | None = typer.Option(None, "--visibility", help="public o private."),
    has_issues: bool = typer.Option(True, "--issues/--no-issues", help="Habilita issues."),
    has_wiki: bool = typer.Option(True, "--wiki/--no-wiki", help="Habilita wiki."),
    has_projects: bool = typer.Option(True, "--projects/--no-projects", help="Habilita proyectos."),
    has_discussions: bool = typer.Option(
        False, "--discussions/--no-discussions", help="Habilita discusiones."
    ),
    auto_init: bool = typer.Option(False, "--init/--no-init", help="Inicializa con README."),
    license_template: str | None = typer.Option(
        None, "--license", help="Plantilla de licencia (spdx_id)."
    ),
    gitignore_template: str | None = typer.Option(
        None, "--gitignore", help="Plantilla de .gitignore."
    ),
):
    """Crea un repositorio en la cuenta del usuario autenticado."""
    enum_value("visibility", visibility, VISIBILITY_CHOICES)

    with github_session() as session:
        repo = repos.create_repository(
            session,
            name=name,
            description=description,
            homepage=homepage,
            visibility=visibility,
            has_issues=has_issues,
            has_wiki=has_wiki,
            has_projects=has_projects,
            has_discussions=has_discussions,
            auto_init=auto_init,
            license_template=license_template,
            gitignore_template=gitignore_template,
        )
    output.info(f"Repositorio creado: {repo.full_name} ({repo.html_url})")


@app.command("rename")
@handle_errors
def rename_repo(
    reference: str = typer.Argument(..., help="Repositorio a renombrar."),
    new_name: str = typer.Argument(..., help="Nuevo nombre del repositorio."),
):
    """Renombra un repositorio."""
    with github_session() as session:
        repo = repos.rename_repository(session, reference, new_name)
    output.info(f"Repositorio renombrado: {repo.full_name} ({repo.html_url})")


@app.command("edit")
@handle_errors
def edit_repo(
    reference: str = typer.Argument(..., help="Repositorio a editar."),
    new_name: str | None = typer.Option(None, "--name", help="Nuevo nombre del repositorio."),
    description: str | None = typer.Option(None, "--description", "-d", help="Nueva descripcion."),
    homepage: str | None = typer.Option(None, "--homepage", help="Nueva pagina principal."),
    visibility: str | None = typer.Option(None, "--visibility", help="public o private."),
    default_branch: str | None = typer.Option(None, "--default-branch", help="Rama por defecto."),
    has_issues: bool | None = typer.Option(
        None, "--issues/--no-issues", help="Habilita o deshabilita issues."
    ),
    has_wiki: bool | None = typer.Option(None, "--wiki/--no-wiki", help="Habilita o deshabilita wiki."),
    has_projects: bool | None = typer.Option(None, "--projects/--no-projects", help="Proyectos."),
    has_discussions: bool | None = typer.Option(
        None, "--discussions/--no-discussions", help="Discusiones."
    ),
    has_downloads: bool | None = typer.Option(
        None, "--downloads/--no-downloads", help="Descargas de releases."
    ),
    is_template: bool | None = typer.Option(
        None, "--template/--no-template", help="Repositorio plantilla."
    ),
    allow_forking: bool | None = typer.Option(
        None, "--allow-forking/--no-allow-forking", help="Permitir forks."
    ),
    allow_squash_merge: bool | None = typer.Option(
        None, "--allow-squash-merge/--no-allow-squash-merge"
    ),
    allow_merge_commit: bool | None = typer.Option(
        None, "--allow-merge-commit/--no-allow-merge-commit"
    ),
    allow_rebase_merge: bool | None = typer.Option(
        None, "--allow-rebase-merge/--no-allow-rebase-merge"
    ),
    delete_branch_on_merge: bool | None = typer.Option(
        None, "--delete-branch-on-merge/--no-delete-branch-on-merge"
    ),
    topics: str | None = typer.Option(
        None, "--topics", help="Reemplaza los topics (separados por comas)."
    ),
    add_topics: str | None = typer.Option(
        None, "--add-topics", help="Anade topics (separados por comas)."
    ),
    remove_topics: str | None = typer.Option(
        None, "--remove-topics", help="Quita topics (separados por comas)."
    ),
):
    """Edita descripcion, pagina principal, topics, visibilidad y demas opciones de la API."""
    enum_value("visibility", visibility, VISIBILITY_CHOICES)
    changes = {
        "name": new_name,
        "description": description,
        "homepage": homepage,
        "visibility": visibility,
        "default_branch": default_branch,
        "has_issues": has_issues,
        "has_wiki": has_wiki,
        "has_projects": has_projects,
        "has_discussions": has_discussions,
        "has_downloads": has_downloads,
        "is_template": is_template,
        "allow_forking": allow_forking,
        "allow_squash_merge": allow_squash_merge,
        "allow_merge_commit": allow_merge_commit,
        "allow_rebase_merge": allow_rebase_merge,
        "delete_branch_on_merge": delete_branch_on_merge,
    }

    with github_session() as session:
        repo, current_topics = repos.update_repository(
            session,
            reference,
            changes={key: value for key, value in changes.items() if value is not None},
            topics=split_topics(topics),
            add_topics=split_topics(add_topics),
            remove_topics=split_topics(remove_topics),
        )

    output.info(f"Repositorio actualizado: {repo.full_name} ({repo.html_url})")
    output.info(f"Topics actuales: {', '.join(current_topics) or '-'}")


@app.command("archive")
@handle_errors
def archive_repo(reference: str = typer.Argument(..., help="Repositorio a archivar.")):
    """Archiva un repositorio (dejandolo en solo lectura)."""
    with github_session() as session:
        repo = repos.set_archived(session, reference, archived=True)
    output.info(f"Repositorio archivado: {repo.full_name}")


@app.command("unarchive")
@handle_errors
def unarchive_repo(reference: str = typer.Argument(..., help="Repositorio a reactivar.")):
    """Reactiva un repositorio archivado."""
    with github_session() as session:
        repo = repos.set_archived(session, reference, archived=False)
    output.info(f"Repositorio reactivado: {repo.full_name}")


@app.command("delete")
@handle_errors
def delete_repo(
    reference: str = typer.Argument(..., help="Repositorio a eliminar."),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Confirma la eliminacion."),
):
    """Elimina un repositorio de forma permanente."""
    with github_session() as session:
        repo, deleted = repos.delete_repository(session, reference, confirmed=confirm)

    if not deleted:
        output.cancelled(
            f"{repo.full_name} no se modifico. Vuelve a ejecutar con --yes para confirmar"
        )
        raise typer.Exit(code=1)
    output.info(f"Repositorio eliminado: {repo.full_name}")


@app.command("license")
@handle_errors
def license_repo(
    reference: str = typer.Argument(..., help="Repositorio a consultar."),
    show_content: bool = typer.Option(False, "--content", help="Muestra el texto completo de la licencia."),
    as_json: bool = typer.Option(False, "--json", help="Muestra la salida en JSON."),
):
    """Consulta la licencia y los datos generales del repositorio."""
    with github_session() as session:
        data, content = repos.license_report(session, reference, include_content=show_content)

    if as_json:
        output.json(data)
        return

    output.field_table(f"{data['full_name']} - licencia", output.license_details(data))
    if content is not None:
        output.detail(f"\n{data['license']['file']}\n")
        output.detail(content.decode("utf-8", errors="replace"))


@app.command("clone")
@handle_errors
def clone_repo(
    reference: str = typer.Argument(..., help="Repositorio a clonar."),
    directory: str | None = typer.Option(None, "--directory", "-C", help="Directorio de destino."),
    branch: str | None = typer.Option(None, "--branch", "-b", help="Rama o tag a clonar."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Reduce la salida de git."),
    depth: int | None = typer.Option(None, "--depth", help="Clonacion superficial."),
):
    """Clona el repositorio con git."""
    output.info(f"Clonando {reference}...")
    with github_session() as session:
        repo, destination = repos.clone_repository(
            session,
            reference,
            directory=directory,
            branch=branch,
            depth=depth,
            quiet=quiet,
        )
    output.info(f"Repositorio clonado en: {destination}")


@app.command("open")
@handle_errors
def open_repo(
    reference: str = typer.Argument(..., help="Repositorio a abrir en el navegador."),
    print_url: bool = typer.Option(False, "--print", help="Muestra la URL en lugar de abrir el navegador."),
):
    """Abre la pagina del repositorio en Brave."""
    with github_session() as session:
        if print_url:
            output.info(repos.repository_url(session, reference))
            return
        repo, launcher = repos.open_repository(session, reference)
    output.info(f"Abriendo {repo.html_url} con {launcher}")