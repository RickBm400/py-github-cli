import os
import sys

from dotenv import load_dotenv
from github import Auth, Github

load_dotenv()


def getGithubClient():
    print("Getting Github Client...", file=sys.stderr)
    return _authenticate()


def _authenticate():
    token = os.getenv("GH_TOKEN")
    if not token:
        raise ValueError("GH_TOKEN no esta definido. Configuralo en el archivo .env o en el entorno.")
    auth = Auth.Token(token)
    g = Github(auth=auth)
    return g
