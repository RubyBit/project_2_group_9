import requests
import csv
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

# ----- Configuration for GitHub -----
# Set your GitHub API token in the .env file as GITHUB_TOKEN=your_token_here
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
    "Accept": "application/vnd.github.v3+json"
}

def get_github_repos(org):
    """Fetch all repositories for a GitHub organization."""
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{org}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=GITHUB_HEADERS)
        if response.status_code != 200:
            print(f"Error fetching GitHub repos for {org}: {response.status_code}")
            break
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
        time.sleep(1)  # Respect rate limits
    return repos

# ----- Configuration for GitLab -----
# Set your GitLab API token in the .env file as GITLAB_TOKEN=your_token_here
# You can also set the base URL (e.g., "https://gitlab.com" or your own instance)
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN", "")
GITLAB_URL = os.getenv("GITLAB_URL", "https://gitlab.com")
GITLAB_HEADERS = {
    "PRIVATE-TOKEN": GITLAB_TOKEN,
    "Accept": "application/json"
}

def get_gitlab_repos(group):
    """Fetch all repositories (projects) for a GitLab group.
       The group is looked up by its path.
    """
    # First, look up the group info by its URL-encoded path
    encoded_group = requests.utils.quote(group, safe='')
    group_info_url = f"{GITLAB_URL}/api/v4/groups/{encoded_group}"
    response = requests.get(group_info_url, headers=GITLAB_HEADERS)
    if response.status_code != 200:
        print(f"Error fetching GitLab group info for {group}: {response.status_code}")
        return []
    group_id = response.json()['id']
    
    # Then, get all projects in the group (including subgroups)
    repos = []
    page = 1
    while True:
        url = f"{GITLAB_URL}/api/v4/groups/{group_id}/projects?include_subgroups=true&per_page=100&page={page}"
        response = requests.get(url, headers=GITLAB_HEADERS)
        if response.status_code != 200:
            print(f"Error fetching GitLab repos for group {group}: {response.status_code}")
            break
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
        time.sleep(1)
    return repos

def generate_csv(platform, orgs, output_file):
    """
    Generate a CSV file with columns: country, org/group, repo_link.
    The parameter 'orgs' is a list of tuples (country, org_or_group_name).
    The 'platform' parameter should be either "github" or "gitlab".
    """
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["country", "org/group", "repo_link"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for country, name in orgs:
            if platform.lower() == "github":
                repos = get_github_repos(name)
                for repo in repos:
                    writer.writerow({
                        "country": country,
                        "org/group": name,
                        "repo_link": repo.get("html_url", "")
                    })
            elif platform.lower() == "gitlab":
                repos = get_gitlab_repos(name)
                for repo in repos:
                    writer.writerow({
                        "country": country,
                        "org/group": name,
                        "repo_link": repo.get("web_url", "")
                    })
            else:
                print(f"Unsupported platform: {platform}")
    print(f"CSV file generated: {output_file}")

def main():
    # Choose the platform: either "github" or "gitlab"
    platform = "github"  # Change to "gitlab" if needed

    # List of organizations or groups as tuples: (country, org/group name)
    if platform.lower() == "github":
        orgs = [
            ("USA", "usagov"),
            ("Greece", "eellak")
            # Add more GitHub orgs as needed
        ]
    elif platform.lower() == "gitlab":
        orgs = [
            ("etsi", "osl")
            # Add more GitLab groups as needed
        ]
    else:
        print("Please set platform to either 'github' or 'gitlab'.")
        return

    output_file = "repo_links.csv"
    generate_csv(platform, orgs, output_file)

if __name__ == "__main__":
    main()
