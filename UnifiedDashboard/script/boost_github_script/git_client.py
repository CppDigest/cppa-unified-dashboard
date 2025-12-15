"""
GitHub API Client with GraphQL and REST support
Handles rate limiting and provides unified interface
"""
import time
import requests
from typing import Dict, List, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimitException(Exception):
    """Raised when rate limit is exceeded"""
    pass


class GitHubAPIClient:
    """GitHub API client with GraphQL and REST support"""

    def __init__(self, token: str):
        self.token = token
        self.rest_base_url = "https://api.github.com"
        self.graphql_url = "https://api.github.com/graphql"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        })
        self.rate_limit_remaining = None
        self.rate_limit_reset_time = None

    def _check_rate_limit(self):
        """Check current rate limit status"""
        response = self.session.get(f"{self.rest_base_url}/rate_limit")
        if response.status_code == 200:
            data = response.json()
            self.rate_limit_remaining = data["resources"]["core"]["remaining"]
            self.rate_limit_reset_time = data["resources"]["core"]["reset"]

            if self.rate_limit_remaining == 0:
                wait_time = self.rate_limit_reset_time - int(time.time())
                if wait_time > 0:
                    raise RateLimitException(
                        f"Rate limit exceeded. Reset at {datetime.fromtimestamp(self.rate_limit_reset_time)}. "
                        f"Wait {wait_time} seconds."
                    )
        return True

    def _handle_rate_limit(self, wait_time: int, max_delay: int = 3600):
        """Handle rate limit by waiting with exponential backoff"""
        if wait_time > max_delay:
            wait_time = max_delay

        logger.warning(f"Rate limit hit. Waiting {wait_time} seconds...")
        logger.info(f"Resume time: {datetime.fromtimestamp(time.time() + wait_time)}")

        # Save state before waiting
        time.sleep(wait_time)

        # Recheck rate limit
        self._check_rate_limit()

    def rest_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make REST API request with rate limit handling"""
        self._check_rate_limit()

        url = f"{self.rest_base_url}{endpoint}"
        response = self.session.get(url, params=params)

        if response.status_code == 403:
            # Check if it's rate limit
            if "X-RateLimit-Remaining" in response.headers:
                remaining = int(response.headers["X-RateLimit-Remaining"])
                if remaining == 0:
                    reset_time = int(response.headers["X-RateLimit-Reset"])
                    wait_time = reset_time - int(time.time()) + 10  # Add 10s buffer
                    self._handle_rate_limit(wait_time)
                    # Retry the request
                    return self.rest_request(endpoint, params)

        response.raise_for_status()

        # Update rate limit info
        if "X-RateLimit-Remaining" in response.headers:
            self.rate_limit_remaining = int(response.headers["X-RateLimit-Remaining"])
            self.rate_limit_reset_time = int(response.headers["X-RateLimit-Reset"])

        return response.json()

    def graphql_request(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Make GraphQL API request with rate limit handling"""
        self._check_rate_limit()

        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = self.session.post(
            self.graphql_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 403:
            # Check if it's rate limit
            if "X-RateLimit-Remaining" in response.headers:
                remaining = int(response.headers["X-RateLimit-Remaining"])
                if remaining == 0:
                    reset_time = int(response.headers["X-RateLimit-Reset"])
                    wait_time = reset_time - int(time.time()) + 10  # Add 10s buffer
                    self._handle_rate_limit(wait_time)
                    # Retry the request
                    return self.graphql_request(query, variables)

        response.raise_for_status()
        data = response.json()

        # Check for GraphQL errors
        if "errors" in data:
            error_msg = "; ".join([e.get("message", "Unknown error") for e in data["errors"]])
            raise Exception(f"GraphQL errors: {error_msg}")

        # Update rate limit info
        if "X-RateLimit-Remaining" in response.headers:
            self.rate_limit_remaining = int(response.headers["X-RateLimit-Remaining"])
            self.rate_limit_reset_time = int(response.headers["X-RateLimit-Reset"])

        return data

    def get_repository_info(self, owner: str, repo: str) -> Dict:
        """Get repository information"""
        return self.rest_request(f"/repos/{owner}/{repo}")

    def get_submodules_from_file(self, filepath: str, default_owner: str = None) -> List[Dict]:
        """Get submodules from a local .gitmodules file"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                gitmodules_content = f.read()
        except FileNotFoundError:
            logger.warning(f"Local .gitmodules file not found: {filepath}")
            return []
        except Exception as e:
            logger.error(f"Error reading .gitmodules file {filepath}: {e}")
            return []

        return self._parse_gitmodules(gitmodules_content, default_owner)

    def _parse_gitmodules(self, gitmodules_content: str, default_owner: str = None) -> List[Dict]:
        """Parse .gitmodules file content"""
        submodules = []
        current_submodule = {}

        for line in gitmodules_content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # Skip empty lines and comments

            if line.startswith("[submodule"):
                if current_submodule:
                    submodules.append(current_submodule)
                current_submodule = {}
            elif line.startswith("path ="):
                current_submodule["path"] = line.split("=", 1)[1].strip()
            elif line.startswith("url ="):
                url = line.split("=", 1)[1].strip()
                current_submodule["url"] = url

                # Handle relative URLs (e.g., ../system.git -> boostorg/system)
                if url.startswith("../") or url.startswith("./"):
                    # Relative URL - extract repo name and use default owner
                    repo_name = url.replace("../", "").replace("./", "").replace(".git", "")
                    if default_owner:
                        current_submodule["owner"] = default_owner
                        current_submodule["repo"] = repo_name
                        logger.debug(f"Resolved relative URL {url} -> {default_owner}/{repo_name}")
                # Extract owner/repo from URL (handle various formats)
                # Formats: https://github.com/owner/repo.git
                #         git@github.com:owner/repo.git
                #         https://github.com/owner/repo
                elif "github.com" in url:
                    # Remove .git suffix
                    url_clean = url.replace(".git", "")
                    # Handle SSH format (git@github.com:owner/repo)
                    if url_clean.startswith("git@"):
                        url_clean = url_clean.replace("git@github.com:", "https://github.com/")
                    # Extract path after github.com
                    if "github.com/" in url_clean:
                        path = url_clean.split("github.com/", 1)[1]
                        parts = path.split("/")
                        if len(parts) >= 2:
                            current_submodule["owner"] = parts[0]
                            current_submodule["repo"] = parts[1]

        if current_submodule:
            submodules.append(current_submodule)

        return submodules

    def get_submodules(self, owner: str, repo: str, local_file: str = None) -> List[Dict]:
        """Get submodules from .gitmodules file (local file or GitHub API)"""
        # Try local file first if provided
        if local_file:
            logger.info(f"Reading submodules from local file: {local_file}")
            submodules = self.get_submodules_from_file(local_file, default_owner=owner)
            if submodules:
                logger.info(f"Found {len(submodules)} submodule(s) from local file")
                return submodules
            else:
                logger.info("No submodules found in local file, trying GitHub API...")

        # Fall back to GitHub API
        try:
            # Try to get .gitmodules file
            # GitHub API endpoint: /repos/{owner}/{repo}/contents/{path}
            content = self.rest_request(f"/repos/{owner}/{repo}/contents/.gitmodules")

            # Handle case where API returns a list (shouldn't happen for a file, but just in case)
            if isinstance(content, list):
                logger.warning(f"GitHub API returned a list instead of file object for .gitmodules in {owner}/{repo}")
                return []

            if content.get("type") == "file":
                # Decode base64 content
                import base64
                try:
                    gitmodules_content = base64.b64decode(content["content"]).decode("utf-8")
                except Exception as e:
                    logger.error(f"Failed to decode .gitmodules content for {owner}/{repo}: {e}")
                    return []

                # Parse using shared method
                submodules = self._parse_gitmodules(gitmodules_content, default_owner=owner)
                logger.info(f"Found {len(submodules)} submodule(s) in {owner}/{repo} via API")
                return submodules
            else:
                logger.warning(f".gitmodules is not a file (type: {content.get('type')}) in {owner}/{repo}")
                return []
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.debug(f"No .gitmodules file found in {owner}/{repo}")
                return []
            else:
                logger.error(f"HTTP error getting .gitmodules for {owner}/{repo}: {e.response.status_code} - {e}")
                raise
        except Exception as e:
            logger.error(f"Error getting submodules for {owner}/{repo}: {e}")
            return []

