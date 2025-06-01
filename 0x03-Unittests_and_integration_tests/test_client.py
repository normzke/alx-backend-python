#!/usr/bin/env python3
"""Unit tests for GithubOrgClient class.
"""
import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class.
    """
    @parameterized.expand([
        ('google', {'login': 'google'}),
        ('abc', {'login': 'abc'}),
    ])
    @patch('client.get_json')
    def test_org(self, org, expected, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value.

        Args:
            org: The organization name
            expected: The expected response
            mock_get_json: The mocked get_json function
        """
        mock_get_json.return_value = expected
        client = GithubOrgClient(org)
        self.assertEqual(client.org, expected)
        mock_get_json.assert_called_once_with(
            f'https://api.github.com/orgs/{org}'
        )

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the correct value."""
        with patch.object(
            GithubOrgClient,
            'org',
            new_callable=PropertyMock,
            return_value={
                'repos_url': 'https://api.github.com/orgs/google/repos'
            }
        ) as mock_org:
            client = GithubOrgClient('google')
            self.assertEqual(
                client._public_repos_url,
                'https://api.github.com/orgs/google/repos'
            )

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns the correct value.

        Args:
            mock_get_json: The mocked get_json function
        """
        test_payload = [
            {'name': 'repo1', 'license': {'key': 'mit'}},
            {'name': 'repo2', 'license': {'key': 'apache-2.0'}},
            {'name': 'repo3', 'license': {'key': 'gpl'}},
        ]
        mock_get_json.return_value = test_payload
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock,
            return_value='https://api.github.com/orgs/google/repos'
        ) as mock_url:
            client = GithubOrgClient('google')
            self.assertEqual(
                client.public_repos(),
                ['repo1', 'repo2', 'repo3']
            )
            mock_get_json.assert_called_once_with(mock_url.return_value)

    @patch('client.get_json')
    def test_public_repos_with_license(self, mock_get_json):
        """Test that public_repos with license filter returns
the correct value.

        Args:
            mock_get_json: The mocked get_json function
        """
        test_payload = [
            {'name': 'repo1', 'license': {'key': 'mit'}},
            {'name': 'repo2', 'license': {'key': 'apache-2.0'}},
            {'name': 'repo3', 'license': {'key': 'gpl'}},
        ]
        mock_get_json.return_value = test_payload
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock,
            return_value='https://api.github.com/orgs/google/repos'
        ) as mock_url:
            client = GithubOrgClient('google')
            self.assertEqual(
                client.public_repos(license="apache-2.0"),
                ['repo2']
            )
            mock_get_json.assert_called_once_with(mock_url.return_value)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that has_license returns the correct value.

        Args:
            repo: The repository dictionary
            license_key: The license key to check
            expected: The expected result
        """
        client = GithubOrgClient('google')
        self.assertEqual(
            client.has_license(repo, license_key),
            expected
        )
