import os
import shutil
import subprocess
import webbrowser
from pathlib import Path

from .exceptions import BrowserNotFoundError

BRAVE_WINDOWS_PATHS = (
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
)
BROWSER_ENV_VAR = "GHM_BROWSER"


def is_wsl() -> bool:
    if os.getenv("WSL_DISTRO_NAME") or os.getenv("WSL_INTEROP"):
        return True
    uname = os.uname()
    return "microsoft" in f"{uname.sysname} {uname.release} {uname.version}".lower()


def wsl_path(windows_path: str) -> str:
    drive, _, rest = windows_path.partition(":")
    return f"/mnt/{drive.lower()}{rest.replace(chr(92), '/')}"


def brave_executable() -> str | None:
    override = os.getenv(BROWSER_ENV_VAR)
    if override:
        resolved = shutil.which(override) or (override if Path(override).is_file() else None)
        if resolved:
            return resolved
    if is_wsl():
        candidates = [wsl_path(path) for path in BRAVE_WINDOWS_PATHS]
        local_app_data = os.getenv("LOCALAPPDATA")
        if local_app_data:
            candidates.append(
                wsl_path(os.path.join(local_app_data, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"))
            )
        for candidate in candidates:
            if Path(candidate).is_file():
                return candidate
    return shutil.which("brave") or shutil.which("brave-browser")


def launcher_candidates(url: str) -> list[list[str]]:
    commands: list[list[str]] = []
    brave = brave_executable()
    if brave:
        commands.append([brave, url])
    if is_wsl():
        commands.append(["wslview", url])
        commands.append(["powershell.exe", "-NoProfile", "-Command", "Start-Process", url])
    return commands


def open_url(url: str) -> str:
    for command in launcher_candidates(url):
        if not shutil.which(command[0]) and not Path(command[0]).is_file():
            continue
        try:
            subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return command[0]
        except OSError:
            continue
    try:
        if webbrowser.open(url):
            return "navegador del sistema"
    except webbrowser.Error:
        pass
    raise BrowserNotFoundError(
        "no se pudo abrir ningun navegador",
        hint="instala Brave o define GHM_BROWSER con la ruta del ejecutable",
        details=[f"URL: {url}"],
    )