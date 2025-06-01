#!/usr/bin/env python3
"""GithubOrgClient class for accessing GitHub organization data.
"""
from typing import List, Dict
from utils import get_json


class GithubOrgClient:
    """A client for accessing GitHub organization data.
    """
    def __init__(self, org_name: str) -> None:
        """Initialize the client with an organization name.

        Args:
            org_name: The name of the GitHub organization
        """
        self._org_name = org_name
        self._org = None
        self._repos_url = None

    @property
    def org(self) -> Dict:
        """Get the organization data.

        Returns:
            Dict: The organization data
        """
        if self._org is None:
            self._org = get_json(f'https://api.github.com/orgs/{self._org_name}')
        return self._org

    @property
    def _public_repos_url(self) -> str:
        """Get the URL for the organization's public repositories.

        Returns:
            str: The URL for the organization's public repositories
        """
        if self._repos_url is None:
            self._repos_url = self.org['repos_url']
        return self._repos_url

    def public_repos(self, license: str = None) -> List[str]:
        """Get the list of public repositories.

        Args:
            license: Optional license key to filter repositories

        Returns:
            List[str]: List of repository names
        """
        repos = get_json(self._public_repos_url)
        if license:
            return [repo['name'] for repo in repos if self.has_license(repo, license)]
        return [repo['name'] for repo in repos]

    @staticmethod
    def has_license(repo: Dict, license_key: str) -> bool:
        """Check if a repository has a specific license.

        Args:
            repo: The repository data
            license_key: The license key to check for

        Returns:
            bool: True if the repository has the specified license
        """
        if not repo.get('license'):
            return False
        return repo['license'].get('key') == license_key 