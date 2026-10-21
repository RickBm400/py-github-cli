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
uv run start
```

## Project structure

```
src/terminal_github_manager/
├── main.py            # Entry point
├── github_client.py   # GitHub API client and authentication
└── __init__.py
```