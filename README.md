# terminal-github-manager

A command line tool to manage GitHub repositories from your terminal.

## Stack

- **Python 3.13**
- **Typer** — CLI interface
- **PyGithub** — GitHub API client
- **python-dotenv** — environment variable loading
- **uv** — dependency and environment management

## Installation

```bash
uv sync
```

## Configuration

Create a `.env` file in the project root and add your GitHub personal access token:

```
GH_TOKEN=your_token_here
```

The token needs read access to your repositories.

## Usage

```bash
uv run start --help          # ayuda general
uv run start repo --help     # comandos de repositorios
uv run start repo list -n 10
uv run start repo view mi-api
uv run start repo create mi-api --private --init --license mit
uv run start repo edit mi-api --description "API for my project" --add-topics python,api
uv run start repo archive mi-api
uv run start repo license mi-api --content
uv run start repo clone mi-api -C ~/Projects
uv run start repo open mi-api
```

## Project structure

```
src/terminal_github_manager/
├── main.py                  # Entry point: app Typer raiz
├── github_client.py         # Autenticacion y cliente de GitHub
├── exceptions.py            # Errores de dominio y traduccion de la API
├── output.py                # Presentacion: tablas, JSON y mensajes
├── browser.py               # Apertura de URLs (Brave, WSL)
├── cli/
│   ├── options.py           # Validacion de opciones y manejo de errores
│   └── repos.py             # Declaracion de comandos Typer
└── services/
    ├── github_session.py    # Sesion autenticada con el usuario del token
    └── repository_service.py# Logica de repositorios
```