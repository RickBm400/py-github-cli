import itertools
import shutil
import subprocess

from github import AuthenticatedUser, Repository, UnknownObjectException

from .. import browser
from ..exceptions import (
    CloneFailedError,
    LicenseNotFoundError,
    OutOfScopeError,
    RepositoryNotFoundError,
)
from .github_session import GitHubSession, api_errors

SUGGESTION_LIMIT = 15


def list_repositories(
    session: GitHubSession,
    *,
    affiliation: str,
    visibility: str | None,
    sort: str,
    direction: str,
    archived: bool | None,
    limit: int,
) -> list[Repository]:
    with api_errors(f"no se pudo listar los repositorios (affiliation='{affiliation}')"):
        params: dict = {"affiliation": affiliation, "sort": sort, "direction": direction}
        if visibility is not None:
            params["visibility"] = visibility
        repositories = session.user.get_repos(**params)
        repositories = (repo for repo in repositories if archived is None or repo.archived == archived)
        if limit > 0:
            repositories = itertools.islice(repositories, limit)
        return list(repositories)


def resolve_repository(session: GitHubSession, reference: str) -> Repository:
    user = session.user
    if "/" in reference and reference.split("/", 1)[0].lower() != user.login.lower():
        raise OutOfScopeError(
            f"fuera de alcance: {reference}",
            hint=f"este token solo administra los repositorios de {user.login}",
        )
    try:
        return user.get_repo(reference)
    except UnknownObjectException:
        raise RepositoryNotFoundError(reference, user.login, _available_repositories(user)) from None


def repository_snapshot(repo: Repository) -> dict:
    with api_errors(f"no se pudo leer {repo.full_name}"):
        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "owner": repo.owner.login,
            "description": repo.description,
            "homepage": repo.homepage,
            "private": repo.private,
            "visibility": repo.visibility,
            "archived": repo.archived,
            "language": repo.language,
            "topics": repo.topics,
            "default_branch": repo.default_branch,
            "size_kb": repo.size,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "watchers": repo.subscribers_count,
            "open_issues": repo.open_issues_count,
            "has_issues": repo.has_issues,
            "has_wiki": repo.has_wiki,
            "has_projects": repo.has_projects,
            "has_discussions": getattr(repo, "has_discussions", None),
            "has_downloads": getattr(repo, "has_downloads", None),
            "license": repo.license.name if repo.license else None,
            "created_at": str(repo.created_at),
            "updated_at": str(repo.updated_at),
            "pushed_at": str(repo.pushed_at),
            "url": repo.html_url,
            "clone_url": repo.clone_url,
            "ssh_url": repo.ssh_url,
        }


def create_repository(
    session: GitHubSession,
    *,
    name: str,
    description: str | None = None,
    homepage: str | None = None,
    visibility: str | None = None,
    has_issues: bool = True,
    has_wiki: bool = True,
    has_projects: bool = True,
    has_discussions: bool = False,
    auto_init: bool = False,
    license_template: str | None = None,
    gitignore_template: str | None = None,
) -> Repository:
    if "/" in name:
        raise OutOfScopeError(
            f"nombre de repositorio invalido: '{name}'",
            hint="usa solo el nombre, sin 'owner/repo'",
        )
    options: dict = {
        "description": description,
        "homepage": homepage,
        "has_issues": has_issues,
        "has_wiki": has_wiki,
        "has_projects": has_projects,
        "has_discussions": has_discussions,
        "auto_init": auto_init,
        "license_template": license_template,
        "gitignore_template": gitignore_template,
    }
    if visibility is not None:
        options["private"] = {"public": False, "private": True}[visibility]
    with api_errors(f"no se pudo crear el repositorio '{name}'"):
        return session.user.create_repo(name=name, **options)


def rename_repository(session: GitHubSession, reference: str, new_name: str) -> Repository:
    repo = resolve_repository(session, reference)
    with api_errors(f"no se pudo renombrar {reference} a '{new_name}'"):
        repo.edit(name=new_name)
    return repo


def update_repository(
    session: GitHubSession,
    reference: str,
    *,
    changes: dict,
    topics: list[str] | None = None,
    add_topics: list[str] | None = None,
    remove_topics: list[str] | None = None,
) -> tuple[Repository, list[str]]:
    repo = resolve_repository(session, reference)
    with api_errors(f"no se pudo editar {reference}"):
        if changes:
            repo.edit(**changes)
        if topics is not None:
            repo.replace_topics(topics)
        if add_topics:
            repo.replace_topics([*repo.get_topics(), *add_topics])
        if remove_topics:
            repo.replace_topics([topic for topic in repo.get_topics() if topic not in remove_topics])
        return repo, repo.get_topics()


def set_archived(session: GitHubSession, reference: str, archived: bool) -> Repository:
    repo = resolve_repository(session, reference)
    action = "archivar" if archived else "reactivar"
    with api_errors(f"no se pudo {action} {reference}"):
        repo.edit(archived=archived)
    return repo


def delete_repository(session: GitHubSession, reference: str, confirmed: bool) -> tuple[Repository, bool]:
    repo = resolve_repository(session, reference)
    if not confirmed:
        return repo, False
    with api_errors(f"no se pudo eliminar {reference}"):
        repo.delete()
    return repo, True


def license_report(session: GitHubSession, reference: str, include_content: bool) -> tuple[dict, bytes | None]:
    repo = resolve_repository(session, reference)
    try:
        license_file = repo.get_license()
    except UnknownObjectException:
        raise LicenseNotFoundError(
            f"el repositorio {repo.full_name} no tiene archivo de licencia",
            hint="agrega un archivo LICENSE en la rama por defecto para consultar la licencia",
        ) from None

    with api_errors(f"no se pudo leer la licencia de {reference}"):
        license_info = license_file.license
        data = {
            "full_name": repo.full_name,
            "description": repo.description,
            "visibility": repo.visibility,
            "archived": repo.archived,
            "language": repo.language,
            "default_branch": repo.default_branch,
            "size_kb": repo.size,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "open_issues": repo.open_issues_count,
            "created_at": str(repo.created_at),
            "updated_at": str(repo.updated_at),
            "pushed_at": str(repo.pushed_at),
            "license": {
                "key": license_info.key,
                "name": license_info.name,
                "spdx_id": license_info.spdx_id,
                "url": license_info.url,
                "file": license_file.path,
                "sha": license_file.sha,
                "size": license_file.size,
                "html_url": license_file.html_url,
                "download_url": license_file.download_url,
            },
        }
        content = license_file.decoded_content if include_content else None
    return data, content


def clone_repository(
    session: GitHubSession,
    reference: str,
    *,
    directory: str | None = None,
    branch: str | None = None,
    depth: int | None = None,
    quiet: bool = False,
) -> tuple[Repository, str]:
    if not shutil.which("git"):
        raise CloneFailedError(
            "git no esta instalado o no esta en el PATH",
            hint="instala git o agrega su directorio binario al PATH",
        )
    repo = resolve_repository(session, reference)
    command = ["git", "clone", "--quiet"] if quiet else ["git", "clone"]
    if branch:
        command += ["--branch", branch]
    if depth:
        command += ["--depth", str(depth)]
    command.append(repo.clone_url)
    if directory:
        command.append(directory)
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        raise CloneFailedError(
            f"git termino con codigo {exc.returncode} al clonar {repo.full_name}",
            hint="revisa la red, las credenciales o si el directorio destino ya existe",
        ) from None
    except OSError as exc:
        raise CloneFailedError(
            f"no se pudo ejecutar git para clonar {repo.full_name}",
            hint=str(exc),
        ) from None
    return repo, directory or repo.name


def open_repository(session: GitHubSession, reference: str) -> tuple[Repository, str]:
    repo = resolve_repository(session, reference)
    return repo, browser.open_url(repo.html_url)


def repository_url(session: GitHubSession, reference: str) -> str:
    return resolve_repository(session, reference).html_url


def _available_repositories(user: AuthenticatedUser) -> list[str]:
    with api_errors("no se pudieron obtener los repositorios disponibles"):
        return [repo.full_name for repo in itertools.islice(user.get_repos(affiliation="owner"), SUGGESTION_LIMIT)]