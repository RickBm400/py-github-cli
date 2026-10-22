import os
import sys

from dotenv import find_dotenv, load_dotenv
from github import Auth, Github

load_dotenv(find_dotenv(usecwd=True))


def getGithubClient(token: str | None = None):
    print("Getting Github Client...", file=sys.stderr)
    return _authenticate(token)


def _authenticate(token: str | None = None):
    token = token or os.getenv("GH_TOKEN")
    if not token:
        raise ValueError("GH_TOKEN no esta definido. Configuralo en el archivo .env o en el entorno.")
    auth = Auth.Token(token)
    g = Github(auth=auth)
    return g