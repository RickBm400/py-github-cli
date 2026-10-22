import os
import sys
from pathlib import Path

APP_NAME = "ghm"
ENV_VAR = "GH_TOKEN"
CONFIG_FILENAME = "config"
DIR_MODE = 0o700
FILE_MODE = 0o600
COMMENT = f"# {ENV_VAR} for {APP_NAME}"


def config_dir() -> Path:
    base = os.getenv("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base).expanduser() / APP_NAME


def config_path() -> Path:
    return config_dir() / CONFIG_FILENAME


def token_from_env() -> str | None:
    return (os.getenv(ENV_VAR) or "").strip() or None


def token_from_file() -> str | None:
    path = config_path()
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        if key.strip() == ENV_VAR and value.strip():
            return value.strip().strip("\"'")
    return None


def load_token() -> str | None:
    return token_from_env() or token_from_file()


def save_token(token: str) -> Path:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True, mode=DIR_MODE)
    kept = _other_entries(path)
    kept.append(f"{ENV_VAR}={token.strip()}")
    path.write_text("\n".join([COMMENT, *kept]) + "\n", encoding="utf-8")
    path.chmod(FILE_MODE)
    return path


def token_source() -> str | None:
    if token_from_env():
        return "variable de entorno"
    if token_from_file():
        return str(config_path())
    return None


def is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def _other_entries(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#") and not line.strip().startswith(f"{ENV_VAR}=")
    ]