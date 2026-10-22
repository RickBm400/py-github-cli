from github import GithubException

STATUS_HINTS = {
    401: "token invalido, expirado o revocado. Revisa GH_TOKEN en el archivo .env",
    403: "el token no tiene permisos para esta operacion. Se requiere el scope 'repo'",
    404: "el recurso no existe o no es visible para este token",
    405: "el endpoint no admite esta operacion para el repositorio indicado",
    409: "el repositorio esta en un estado que no permite la operacion",
    422: "GitHub rechazo los datos enviados. Revisa los valores de las opciones",
    451: "el repositorio no esta disponible por motivos legales o de cumplimiento",
}

DEFAULT_DOCUMENTATION = "https://docs.github.com/rest"


class GitHubManagerError(Exception):
    """Error de dominio con mensaje, ayuda, detalles y documentacion."""

    def __init__(
        self,
        message: str,
        hint: str | None = None,
        details: tuple[str, ...] | list[str] = (),
        documentation: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint
        self.details = tuple(details)
        self.documentation = documentation


class MissingTokenError(GitHubManagerError):
    def __init__(self) -> None:
        super().__init__(
            "no se encontro ningun token de GitHub",
            hint=(
                "define GH_TOKEN, guarda el token en ~/.config/ghm/config o ejecuta "
                "'ghm login' desde una terminal interactiva"
            ),
        )


class AuthenticationError(GitHubManagerError):
    pass


class InvalidOptionError(GitHubManagerError):
    pass


class OutOfScopeError(GitHubManagerError):
    pass


class RepositoryNotFoundError(GitHubManagerError):
    def __init__(self, reference: str, login: str, available: list[str]) -> None:
        details = [f"repositorios de {login}: {', '.join(available)}"] if available else []
        super().__init__(
            f"el repositorio '{reference}' no existe o no es visible para este token",
            hint="usa 'ghm repo list' para ver los repositorios disponibles",
            details=details,
        )


class LicenseNotFoundError(GitHubManagerError):
    pass


class CloneFailedError(GitHubManagerError):
    pass


class BrowserNotFoundError(GitHubManagerError):
    pass


def from_github_exception(exc: GithubException, context: str | None = None) -> GitHubManagerError:
    status = getattr(exc, "status", None)
    data = exc.data if isinstance(exc.data, dict) else {}
    api_message = data.get("message") or ""
    if status == 403 and "rate limit" in api_message.lower():
        hint = "se alcanzo el limite de peticiones de la API de GitHub. Espera o reduce el numero de llamadas"
    else:
        hint = STATUS_HINTS.get(status, "GitHub rechazo la operacion. Revisa el estado del repositorio")
    details = [api_message] if api_message else []
    for error in data.get("errors") or []:
        field = error.get("field") or error.get("resource") or "campo"
        details.append(f"{field}: {error.get('code') or error.get('message') or error}")
    return GitHubManagerError(
        context or "GitHub rechazo la operacion",
        hint=hint,
        details=details,
        documentation=data.get("documentation_url") or DEFAULT_DOCUMENTATION,
    )


def from_assertion(exc: AssertionError, context: str | None = None) -> GitHubManagerError:
    return GitHubManagerError(
        context or "valor no soportado por la API de GitHub",
        hint=f"el valor '{exc}' no es aceptado por la biblioteca cliente",
    )