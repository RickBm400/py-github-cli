from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from github import AuthenticatedUser, Github, GithubException

from .. import config, github_client as gh, prompts
from ..exceptions import (
    AuthenticationError,
    MissingTokenError,
    from_assertion,
    from_github_exception,
)


@dataclass
class GitHubSession:
    client: Github
    user: AuthenticatedUser
    token_source: str


@contextmanager
def github_session() -> Iterator[GitHubSession]:
    token, source = resolve_token()
    try:
        client = gh.getGithubClient(token)
    except Exception as exc:
        raise AuthenticationError(
            "no se pudo autenticar el cliente de GitHub",
            hint=str(exc),
        ) from None
    try:
        yield GitHubSession(client=client, user=_authenticated_user(client), token_source=source)
    finally:
        client.close()


@contextmanager
def api_errors(context: str) -> Iterator[None]:
    try:
        yield
    except GithubException as exc:
        raise from_github_exception(exc, context) from None
    except AssertionError as exc:
        raise from_assertion(exc, context) from None


def resolve_token() -> tuple[str, str]:
    token = config.load_token()
    if token:
        return token, config.token_source() or "config"

    token = prompts.ask_token()
    if token:
        path = config.save_token(token)
        return token, str(path)

    raise MissingTokenError()


def _authenticated_user(client: Github) -> AuthenticatedUser:
    try:
        return client.get_user()
    except GithubException as exc:
        raise from_github_exception(exc, "no se pudo identificar al usuario del token") from None