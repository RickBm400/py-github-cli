# GitSMan

CLI personal para administrar repositorios remotos de GitHub desde la terminal.

## Stack

- **Python 3.13**
- **Typer** — CLI interface
- **PyGithub** — GitHub API client
- **Rich** — tablas y mensajes
- **python-dotenv** — environment variable loading
- **uv** — dependency and environment management

## Installation

Desarrollo en el repositorio:

```bash
uv sync
uv run ghm --help
```

Instalacion local como comando global (`ghm`):

```bash
uv tool install .
uv tool update-shell   # agrega ~/.local/bin al PATH
```

Para actualizar o desinstalar:

```bash
uv tool upgrade ghm     # tras volver a ejecutar uv tool install --force .
uv tool uninstall ghm
```

## Configuration

El token se busca en este orden:

1. Variable de entorno `GH_TOKEN`.
2. Archivo `~/.config/ghm/config` (o `$XDG_CONFIG_HOME/ghm/config`).
3. `.env` en el directorio actual.

Si no se encuentra ninguno, se pide el token de forma interactiva y se guarda en
`~/.config/ghm/config` con permisos `600` (directorio `700`):

```bash
ghm login     # guarda el token de forma explicita
ghm config    # muestra ruta de configuracion y origen del token
```

El token necesita el scope `repo` para administrar repositorios privados y
realizar cambios.

## Usage

```bash
ghm                       # banner + ayuda
ghm banner                # mensaje con la version
ghm version               # solo la version

ghm repo list -n 10
ghm repo list --visibility private --sort pushed
ghm repo view mi-api
ghm repo create mi-api --private --init --license mit
ghm repo edit mi-api --description "API for my project" --add-topics python,api
ghm repo archive mi-api
ghm repo delete mi-api --yes
ghm repo license mi-api --content
ghm repo clone mi-api -C ~/Projects
ghm repo open mi-api
```

## Project structure

```
src/terminal_github_manager/
├── main.py                  # Entry point: app Typer raiz y comandos globales
├── github_client.py         # Autenticacion y cliente de GitHub
├── config.py                # Token: entorno, ~/.config/ghm/config y permisos
├── prompts.py               # Entrada interactiva del token
├── banner.py                # Arte ASCII y version
├── version.py               # Version del paquete
├── exceptions.py            # Errores de dominio y traduccion de la API
├── output.py                # Presentacion: tablas, JSON y mensajes
├── browser.py               # Apertura de URLs (Brave, WSL)
├── cli/
│   ├── meta.py              # Comandos banner, version, login, config
│   ├── options.py           # Validacion de opciones y manejo de errores
│   └── repos.py             # Declaracion de comandos Typer
└── services/
    ├── github_session.py    # Sesion autenticada con el usuario del token
    └── repository_service.py# Logica de repositorios
```