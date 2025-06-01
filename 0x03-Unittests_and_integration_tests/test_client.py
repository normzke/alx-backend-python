#!/usr/bin/env python3
"""Unit tests for GithubOrgClient class.
"""
import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


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

    @parameterized.expand(TEST_PAYLOAD)
    @patch('client.get_json')
    def test_public_repos(self, org_payload, repos_payload, expected_repos, _):
        """Test that public_repos returns the correct value.

        Args:
            org_payload: The organization payload
            repos_payload: The repositories payload
            expected_repos: The expected list of repository names
            _: Unused parameter for apache2_repos
            mock_get_json: The mocked get_json function
        """
        mock_get_json.return_value = repos_payload
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock,
            return_value=org_payload['repos_url']
        ) as mock_url:
            client = GithubOrgClient(org_payload['login'])
            self.assertEqual(
                client.public_repos(),
                expected_repos
            )
            mock_get_json.assert_called_once_with(mock_url.return_value)

    @parameterized.expand(TEST_PAYLOAD)
    @patch('client.get_json')
    def test_public_repos_with_license(
            self, org_payload, repos_payload, _, apache2_repos):
        """Test that public_repos with license filter returns the correct value.

        Args:
            org_payload: The organization payload
            repos_payload: The repositories payload
            _: Unused parameter for expected_repos
            apache2_repos: The expected list of Apache 2.0 repositories
            mock_get_json: The mocked get_json function
        """
        mock_get_json.return_value = repos_payload
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock,
            return_value=org_payload['repos_url']
        ) as mock_url:
            client = GithubOrgClient(org_payload['login'])
            self.assertEqual(
                client.public_repos(license="apache-2.0"),
                apache2_repos
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
