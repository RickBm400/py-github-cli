from . import github_client as gh


def main():
    client = gh.getGithubClient()
    repos = list(client.get_user().get_repos(affiliation="owner"))
    print(*(repo.name for repo in reversed(repos)), sep="\n")

    logRepo = client.get_user().get_repos(affiliation="owner")[1]
    print(f"""
    {logRepo.name} - {logRepo.language}
    {logRepo.description}
    {logRepo.clone_url}
    {logRepo.created_at}
    """)
    client.close()


if __name__ == "__main__":
    main()


def basicRequest():
    import requests

    response = requests.get("https://www.google.com")

    print(f"Status Code: {response.raw}")
