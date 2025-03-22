import requests
import pandas as pd
import datetime
import time
import os
from tqdm import tqdm
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# GitLab API token (create one at https://labs.etsi.org/rep/-/profile/personal_access_tokens)
# Store this in a .env file as GITLAB_TOKEN=your_token_here
TOKEN = os.getenv('GITLAB_TOKEN')

# Set the GitLab instance base URL
GITLAB_URL = "https://labs.etsi.org/rep"  # Change this if using a different GitLab instance

# Headers for GitLab API requests
headers = {
    'PRIVATE-TOKEN': TOKEN if TOKEN else '',  # Use empty string if no token to allow anonymous access
    'Accept': 'application/json'
}

def parse_gitlab_date(date_str):
    """Parse GitLab date string to datetime object, handling different formats"""
    try:
        dt = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        # Fallback to regex parsing if needed
        date_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})'
        match = re.search(date_pattern, date_str)
        if match:
            dt = datetime.datetime.strptime(match.group(1), '%Y-%m-%dT%H:%M:%S')
        else:
            raise ValueError("Date format not recognized")

    # Ensure the datetime is timezone-aware. If tzinfo is None, assume UTC.
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt

def get_groups(parent_id=None):
    """Get all groups from GitLab instance, optionally within a parent group"""
    groups = []
    page = 1
    while True:
        url = f'{GITLAB_URL}/api/v4/groups'
        if parent_id:
            url += f'?parent_id={parent_id}'
        
        url += f'{"&" if parent_id else "?"}per_page=100&page={page}'
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching groups: {response.status_code}")
            print(response.json())
            break
        
        current_groups = response.json()
        if not current_groups:
            break
            
        groups.extend(current_groups)
        page += 1
        
        # Respect GitLab's rate limiting
        time.sleep(1)
        
    return groups

def get_repos(group_id=None):
    repos = []
    page = 1
    while True:
        if group_id:
            url = f'{GITLAB_URL}/api/v4/groups/{group_id}/projects?include_subgroups=true&per_page=100&page={page}'
        else:
            url = f'{GITLAB_URL}/api/v4/projects?per_page=100&page={page}'

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching repos for group {group_id}: {response.status_code}")
            print(response.json())
            break

        current_repos = response.json()
        if not current_repos:
            break

        repos.extend(current_repos)
        page += 1

        # Respect GitLab's rate limiting
        time.sleep(1)

    return repos

def get_contributors(project_id):
    """Get contributors for a repository"""
    contributors = []
    page = 1
    while True:
        response = requests.get(
            f'{GITLAB_URL}/api/v4/projects/{project_id}/repository/contributors?per_page=100&page={page}',
            headers=headers
        )
        if response.status_code != 200:
            print(f"Error fetching contributors for project {project_id}: {response.status_code}")
            break
            
        current_contributors = response.json()
        if not current_contributors:
            break
            
        contributors.extend(current_contributors)
        page += 1
        
        # Respect GitLab's rate limiting
        time.sleep(1)
        
    return contributors

def get_issues(project_id):
    """Get issues for a repository"""
    all_issues = {'open': [], 'closed': []}
    
    # Get closed issues
    page = 1
    while True:
        response = requests.get(
            f'{GITLAB_URL}/api/v4/projects/{project_id}/issues?state=closed&per_page=100&page={page}',
            headers=headers
        )
        if response.status_code != 200:
            print(f"Error fetching closed issues for project {project_id}: {response.status_code}")
            break
            
        current_issues = response.json()
        if not current_issues:
            break
            
        all_issues['closed'].extend(current_issues)
        page += 1
        
        # Respect GitLab's rate limiting
        time.sleep(1)
    
    # Get open issues
    page = 1
    while True:
        response = requests.get(
            f'{GITLAB_URL}/api/v4/projects/{project_id}/issues?state=opened&per_page=100&page={page}',
            headers=headers
        )
        if response.status_code != 200:
            print(f"Error fetching open issues for project {project_id}: {response.status_code}")
            break
            
        current_issues = response.json()
        if not current_issues:
            break
            
        all_issues['open'].extend(current_issues)
        page += 1
        
        # Respect GitLab's rate limiting
        time.sleep(1)
        
    return all_issues

def get_merge_requests(project_id):
    """Get merge requests for a repository (GitLab equivalent of pull requests)"""
    all_mrs = {'open': [], 'closed': []}
    
    # Get closed MRs
    page = 1
    while True:
        response = requests.get(
            f'{GITLAB_URL}/api/v4/projects/{project_id}/merge_requests?state=closed&per_page=100&page={page}',
            headers=headers
        )
        if response.status_code != 200:
            print(f"Error fetching closed MRs for project {project_id}: {response.status_code}")
            break
            
        current_mrs = response.json()
        if not current_mrs:
            break
            
        all_mrs['closed'].extend(current_mrs)
        page += 1
        
        # Respect GitLab's rate limiting
        time.sleep(1)
    
    # Get open MRs
    page = 1
    while True:
        response = requests.get(
            f'{GITLAB_URL}/api/v4/projects/{project_id}/merge_requests?state=opened&per_page=100&page={page}',
            headers=headers
        )
        if response.status_code != 200:
            print(f"Error fetching open MRs for project {project_id}: {response.status_code}")
            break
            
        current_mrs = response.json()
        if not current_mrs:
            break
            
        all_mrs['open'].extend(current_mrs)
        page += 1
        
        # Respect GitLab's rate limiting
        time.sleep(1)
        
    return all_mrs

def get_commits(project_id):
    """Get commits for a repository"""
    commits = []
    page = 1
    while True:
        response = requests.get(
            f'{GITLAB_URL}/api/v4/projects/{project_id}/repository/commits?per_page=100&page={page}',
            headers=headers
        )
        if response.status_code != 200:
            print(f"Error fetching commits for project {project_id}: {response.status_code}")
            break
            
        current_commits = response.json()
        if not current_commits:
            break
            
        commits.extend(current_commits)
        page += 1
        
        # Respect GitLab's rate limiting
        time.sleep(1)
        
    return commits

def check_file_exists(project_id, file_path):
    """Check if a file exists in a repository"""
    # URL encode the file path for the API
    encoded_path = requests.utils.quote(file_path, safe='')
    
    response = requests.get(
        f'{GITLAB_URL}/api/v4/projects/{project_id}/repository/files/{encoded_path}?ref=master',
        headers=headers
    )
    if response.status_code != 200:
        # Try with main branch if master doesn't exist
        response = requests.get(
            f'{GITLAB_URL}/api/v4/projects/{project_id}/repository/files/{encoded_path}?ref=main',
            headers=headers
        )
    return response.status_code == 200

def get_ci_pipelines(project_id):
    """Check if the repository has CI/CD pipelines"""
    response = requests.get(
        f'{GITLAB_URL}/api/v4/projects/{project_id}/pipelines',
        headers=headers
    )
    if response.status_code != 200:
        return []
    return response.json()

def calculate_metrics(repos, group_name, org_id):
    """Calculate sustainability metrics for each repository"""
    metrics = []
    current_date = current_date = datetime.datetime.now(datetime.timezone.utc)
    
    for repo in tqdm(repos, desc=f"Processing {group_name} repositories"):
        project_id = repo['id']
        repo_full_path = repo['path_with_namespace']
        
        # Parse the created_at date
        repo_created_at = parse_gitlab_date(repo['created_at'])
        repo_age_days = (current_date - repo_created_at).days
        repo_age_months = repo_age_days / 30.44  # Average days in a month
        
        # Get additional data
        contributors = get_contributors(project_id)
        issues = get_issues(project_id)
        mrs = get_merge_requests(project_id)
        commits = get_commits(project_id)
        
        # Calculate issue resolution time
        issue_resolution_times = []
        for issue in issues['closed']:
            if 'created_at' in issue and 'closed_at' in issue:
                created_at = parse_gitlab_date(issue['created_at'])
                closed_at = parse_gitlab_date(issue['closed_at'])
                resolution_time = (closed_at - created_at).total_seconds() / 3600  # in hours
                issue_resolution_times.append(resolution_time)
        
        avg_issue_resolution_time = sum(issue_resolution_times) / len(issue_resolution_times) if issue_resolution_times else None
        
        # Calculate last commit date
        last_commit_date = None
        last_commit_age = None
        if commits:
            last_commit_date_str = commits[0]['created_at']
            last_commit_date = parse_gitlab_date(last_commit_date_str)
            last_commit_age = (current_date - last_commit_date).days
        
        # Check for documentation files
        has_readme = check_file_exists(project_id, 'README.md')
        has_license = check_file_exists(project_id, 'LICENSE')
        has_contributing = check_file_exists(project_id, 'CONTRIBUTING.md')
        
        # Check for CI/CD
        has_cicd = len(get_ci_pipelines(project_id)) > 0
        
        # Calculate percentage of external contributions
        owner_namespace = repo_full_path.split('/')[0]
        external_mrs = [mr for mr in mrs['closed'] + mrs['open'] 
                       if mr.get('author', {}).get('username', '') != owner_namespace]
        external_mr_percentage = len(external_mrs) / len(mrs['closed'] + mrs['open']) * 100 if len(mrs['closed'] + mrs['open']) > 0 else 0
        
        # Gather metrics
        repo_metrics = {
            'organization': org_id,
            'group_name': group_name,
            'repo_name': repo['name'],
            'repo_full_path': repo_full_path,
            
            # Activity & Maintenance Metrics
            'repo_age_days': repo_age_days,
            'repo_age_months': repo_age_months,
            'commit_frequency_per_month': len(commits) / repo_age_months if repo_age_months > 0 else 0,
            'avg_issue_resolution_time_hours': avg_issue_resolution_time,
            'open_issues_percentage': len(issues['open']) / (len(issues['open']) + len(issues['closed'])) * 100 if (len(issues['open']) + len(issues['closed'])) > 0 else 0,
            'last_commit_date': last_commit_date,
            'days_since_last_commit': last_commit_age,
            
            # Collaboration & Community Engagement
            'num_contributors': len(contributors),
            'num_forks': repo.get('forks_count', 0),
            'num_stars': repo.get('star_count', 0),
            'merged_pr_percentage': len([mr for mr in mrs['closed'] if mr.get('state') == 'merged']) / (len(mrs['closed']) + len(mrs['open'])) * 100 if (len(mrs['closed']) + len(mrs['open'])) > 0 else 0,
            'external_pr_percentage': external_mr_percentage,
            
            # Code & Documentation Quality
            'has_readme': has_readme,
            'has_license': has_license,
            'has_contributing': has_contributing,
            'has_cicd': has_cicd,
            
            # Raw counts for reference
            'total_commits': len(commits),
            'open_issues': len(issues['open']),
            'closed_issues': len(issues['closed']),
            'open_prs': len(mrs['open']),
            'closed_prs': len(mrs['closed'])
        }
        
        metrics.append(repo_metrics)
        
    return metrics

def load_existing_metrics(file_path):
    """Load existing metrics from a CSV file if it exists"""
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None

def save_metrics(metrics, file_path):
    """Append new metrics to the existing CSV file instead of overwriting"""
    new_df = pd.DataFrame(metrics)

    # If the file exists, append data without overwriting
    if os.path.exists(file_path):
        existing_df = pd.read_csv(file_path)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.drop_duplicates(subset=['repo_full_path', 'organization'], keep='last', inplace=True)
        combined_df.to_csv(file_path, index=False)
        return len(new_df), len(combined_df)
    else:
        # If the file doesn't exist, create it
        new_df.to_csv(file_path, index=False)
        return len(new_df), len(new_df)

def process_group(group_id, group_name, org_id, output_file):
    """Process a single GitLab group and add to the combined dataset"""
    print(f"Fetching repositories for group '{group_name}' (ID: {group_id})...")
    repos = get_repos(group_id)
    print(f"Found {len(repos)} repositories in group {group_name}.")
    
    print(f"Calculating sustainability metrics for {group_name}...")
    metrics = calculate_metrics(repos, group_name, org_id)
    
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
        print("Created 'data' directory")
    
    # Save metrics to the combined file
    new_count, total_count = save_metrics(metrics, output_file)
    print(f"Added {new_count} repositories from group {group_name} to dataset. Total repositories: {total_count}")
    
    return metrics

def find_group_by_path(path):
    """Find a GitLab group by its path"""
    parts = path.strip('/').split('/')
    parent_id = None
    group_id = None
    
    # Navigate through the path to find the group
    for part in parts:
        url = f'{GITLAB_URL}/api/v4/groups'
        if parent_id:
            url += f'?parent_id={parent_id}'
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error searching for group: {response.status_code}")
            return None
        
        groups = response.json()
        matching_group = next((g for g in groups if g['path'] == part), None)
        
        if not matching_group:
            print(f"Group part '{part}' not found in path '{path}'")
            return None
        
        group_id = matching_group['id']
        parent_id = group_id
    
    return group_id

def find_group_by_path_direct(path):
    """Find a GitLab group by directly querying its full path"""
    # URL encode the path for the API
    encoded_path = requests.utils.quote(path, safe='')
    
    response = requests.get(
        f'{GITLAB_URL}/api/v4/groups/{encoded_path}',
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()['id']
    else:
        print(f"Group not found with path: {path}")
        print(f"Status code: {response.status_code}")
        # Try listing all groups if the token has sufficient permissions
        all_groups = get_groups()
        print(f"Found {len(all_groups)} groups in total")
        for group in all_groups:
            print(f"Available group: {group['full_path']} (ID: {group['id']})")
        return None

def main():
    """Main function to process GitLab groups"""
    # Define output file path
    output_file = "data/gitlab_repos_sustainability_metrics.csv"
    
    # Define groups to scrape
    # Format: [group_path, organization_identifier]
    # For ETSI OSL, the path would be "osl"
    groups = [
        ["osl", "etsi"],
        # Add more groups/organizations as needed
    ]
    
    # Process each group
    for group_path, org_id in groups:
        # Try to find the group ID based on path
        print(f"Searching for group with path: {group_path}")
        
        # Try the direct path lookup first
        group_id = find_group_by_path_direct(group_path)
        
        # If that fails, try hierarchical lookup
        if not group_id:
            group_id = find_group_by_path(group_path)
        
        if group_id:
            print(f"Found group ID: {group_id}")
            process_group(group_id, group_path, org_id, output_file)
        else:
            print(f"Could not find group with path: {group_path}")
            print("Proceeding to the next group...")
    
    print(f"All metrics saved to {output_file}")

if __name__ == "__main__":
    # Note: Anonymous access is used when no token is provided
    if not TOKEN:
        print("No GitLab API token provided. Using anonymous access (limited rate limits and features).")
    main()