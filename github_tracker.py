"""GitHub API client for tracking repository transfers."""

import requests
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from database import RepoRadarDB

logger = logging.getLogger(__name__)


class GitHubTracker:
    """GitHub API client for tracking repository ownership changes."""

    def __init__(self, token: str, db: RepoRadarDB):
        """Initialize GitHub tracker with API token and database."""
        self.token = token
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        })
        self.rate_limit_reset = 0
        self.remaining_requests = 5000

    def check_rate_limit(self):
        """Check and handle GitHub API rate limits."""
        if self.remaining_requests < 10:
            sleep_time = max(0, self.rate_limit_reset - time.time())
            if sleep_time > 0:
                logger.warning(f"Rate limit reached. Sleeping for {sleep_time} seconds")
                time.sleep(sleep_time + 1)

    def make_request(self, url: str) -> Optional[Dict]:
        """Make a rate-limited request to GitHub API."""
        self.check_rate_limit()
        
        try:
            response = self.session.get(url)
            
            # Update rate limit info
            self.remaining_requests = int(response.headers.get('X-RateLimit-Remaining', 0))
            self.rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 0))
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Resource not found: {url}")
                return None
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None

    def get_repo_info(self, repo_full_name: str) -> Optional[Dict]:
        """Get repository information including owner, stars, and language."""
        url = f"https://api.github.com/repos/{repo_full_name}"
        return self.make_request(url)

    def get_repo_events(self, repo_full_name: str, since: datetime = None) -> List[Dict]:
        """Get repository events, filtering for transfers."""
        if since is None:
            since = datetime.now() - timedelta(hours=1)
            
        url = f"https://api.github.com/repos/{repo_full_name}/events"
        events = self.make_request(url)
        
        if not events:
            return []

        transfer_events = []
        for event in events:
            event_date = datetime.fromisoformat(event['created_at'].replace('Z', '+00:00'))
            if event_date < since:
                continue
                
            # Look for transfer events (repository transfer or ownership change)
            if event['type'] in ['TransferEvent', 'RepositoryEvent']:
                transfer_events.append(event)
                
        return transfer_events

    def get_org_repos(self, org_name: str) -> List[str]:
        """Get list of repository names for an organization."""
        repos = []
        page = 1
        
        while True:
            url = f"https://api.github.com/orgs/{org_name}/repos?page={page}&per_page=100"
            response = self.make_request(url)
            
            if not response or len(response) == 0:
                break
                
            for repo in response:
                repos.append(repo['full_name'])
                
            page += 1
            
        logger.info(f"Found {len(repos)} repositories for org {org_name}")
        return repos

    def detect_ownership_change(self, repo_full_name: str) -> Optional[Dict]:
        """Detect if a repository has changed ownership by comparing with stored data."""
        current_info = self.get_repo_info(repo_full_name)
        if not current_info:
            return None

        current_owner = current_info['owner']['login']
        
        # For this prototype, we'll detect changes by checking if the owner
        # differs from what we might expect based on the repo name
        # In a real implementation, you'd store previous ownership data
        
        # Simple heuristic: if repo name suggests different owner than current
        repo_name_parts = repo_full_name.split('/')
        if len(repo_name_parts) == 2:
            expected_owner, repo_name = repo_name_parts
            if expected_owner.lower() != current_owner.lower():
                return {
                    'repo': repo_full_name,
                    'old_owner': expected_owner,
                    'new_owner': current_owner,
                    'date': datetime.now().isoformat(),
                    'stars': current_info.get('stargazers_count', 0),
                    'language': current_info.get('language', 'Unknown')
                }
        
        return None

    def check_repositories(self, repo_list: List[str]) -> List[Dict]:
        """Check a list of repositories for ownership changes."""
        transfers = []
        
        for repo in repo_list:
            logger.info(f"Checking repository: {repo}")
            
            # Get current repository info
            repo_info = self.get_repo_info(repo)
            if not repo_info:
                continue

            # Check for ownership changes (simplified for prototype)
            transfer = self.detect_ownership_change(repo)
            if transfer:
                transfers.append(transfer)
                
                # Store in database
                self.db.add_transfer(
                    repo=transfer['repo'],
                    old_owner=transfer['old_owner'],
                    new_owner=transfer['new_owner'],
                    date=transfer['date'],
                    stars=transfer['stars'],
                    language=transfer['language']
                )
            
            # Small delay to be respectful to API
            time.sleep(0.1)
            
        return transfers

    def check_organizations(self, org_list: List[str]) -> List[Dict]:
        """Check all repositories in given organizations for transfers."""
        all_transfers = []
        
        for org in org_list:
            logger.info(f"Checking organization: {org}")
            repos = self.get_org_repos(org)
            transfers = self.check_repositories(repos)
            all_transfers.extend(transfers)
            
        return all_transfers