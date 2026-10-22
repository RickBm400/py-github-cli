import typer

app = typer.Typer(
    name="ghm",
    help="terminal-github-manager: gestion de repositorios de GitHub desde la terminal.",
    no_args_is_help=True,
)


def main():
    app()


if __name__ == "__main__":
    main()