import os
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from github import AuthenticatedUser, Github, GithubException

from .. import github_client as gh
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


@contextmanager
def github_session() -> Iterator[GitHubSession]:
    if not os.getenv("GH_TOKEN"):
        raise MissingTokenError()
    try:
        client = gh.getGithubClient()
    except Exception as exc:
        raise AuthenticationError(
            "no se pudo autenticar el cliente de GitHub",
            hint=str(exc),
        ) from None
    try:
        yield GitHubSession(client=client, user=_authenticated_user(client))
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


def _authenticated_user(client: Github) -> AuthenticatedUser:
    try:
        return client.get_user()
    except GithubException as exc:
        raise from_github_exception(exc, "no se pudo identificar al usuario del token") from None