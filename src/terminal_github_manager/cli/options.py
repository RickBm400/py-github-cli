from collections.abc import Callable
from functools import wraps
from typing import Any

import typer

from ..exceptions import GitHubManagerError, InvalidOptionError
from .. import output


def enum_value(option: str, value: str | None, allowed: tuple[str, ...]) -> str | None:
    if value is not None and value not in allowed:
        raise InvalidOptionError(
            f"valor invalido para --{option}: '{value}'",
            hint=f"valores permitidos: {', '.join(allowed)}",
        )
    return value


def split_topics(value: str | None) -> list[str] | None:
    if value is None:
        return None
    return [topic.strip() for topic in value.split(",") if topic.strip()]


def handle_errors(command: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(command)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return command(*args, **kwargs)
        except GitHubManagerError as error:
            output.error(error)
            raise typer.Exit(code=1) from None

    return wrapper