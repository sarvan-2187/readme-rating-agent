import os
import re
import base64
import requests
from crewai.tools import tool

def extract_owner_repo(url: str) -> tuple[str, str]:
    """Extracts owner and repo from a GitHub URL."""
    # Remove trailing .git if present
    if url.endswith(".git"):
        url = url[:-4]
    # Remove trailing slash if present
    if url.endswith("/"):
        url = url[:-1]
        
    pattern = r"github\.com/([^/]+)/([^/]+)"
    match = re.search(pattern, url)
    if not match:
        raise ValueError("Invalid GitHub URL format. Expected something like 'https://github.com/owner/repo'")
    
    return match.group(1), match.group(2)

@tool("Read GitHub Repository README")
def fetch_readme_content(github_url: str) -> str:
    """
    Fetches the content of the README file from a GitHub repository URL.
    Input should be a valid GitHub repository URL.
    Returns the decoded content of the README as a string, or an error message if not found.
    """
    try:
        owner, repo = extract_owner_repo(github_url)
    except ValueError as e:
        return str(e)
    
    api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            return f"Error: README not found for repository '{owner}/{repo}'."
        elif response.status_code == 403:
            return f"Error: API rate limit exceeded or access forbidden."
        
        response.raise_for_status()
        
        data = response.json()
        
        if "content" in data and "encoding" in data:
            if data["encoding"] == "base64":
                content_bytes = base64.b64decode(data["content"])
                return content_bytes.decode("utf-8", errors="replace")
            else:
                return f"Error: Unsupported encoding '{data['encoding']}'."
        else:
            return "Error: Unexpected response format from GitHub API."
            
    except requests.exceptions.RequestException as e:
        return f"Error fetching from GitHub API: {str(e)}"
