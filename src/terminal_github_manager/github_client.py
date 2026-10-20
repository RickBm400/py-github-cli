import os

from dotenv import load_dotenv
from github import Auth, Github

load_dotenv()


def getGithubClient():
    print("Getting Github Client...")
    return _authenticate()


def _authenticate():
    token = os.getenv("GH_TOKEN")
    auth = Auth.Token(token)
    g = Github(auth=auth)
    return g
