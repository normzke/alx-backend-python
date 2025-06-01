#!/usr/bin/env python3
"""Unit tests for client module.
"""
import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, Mock, PropertyMock
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient class.
    """
    
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value.
        
        Args:
            org_name: The name of the organization to test
            mock_get_json: The mocked get_json function
        """
        # Set up the mock return value
        mock_get_json.return_value = {"name": org_name}
        
        # Create an instance of GithubOrgClient
        client = GithubOrgClient(org_name)
        
        # Call the org property
        result = client.org
        
        # Assert that get_json was called once with the correct URL
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        
        # Assert that the result matches the mock return value
        self.assertEqual(result, {"name": org_name})

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the correct URL."""
        # Test payload with repos_url
        test_payload = {
            "repos_url": "https://api.github.com/orgs/test-org/repos"
        }
        
        # Create an instance of GithubOrgClient
        client = GithubOrgClient("test-org")
        
        # Patch the org property to return our test payload
        with patch.object(
            GithubOrgClient,
            'org',
            new_callable=PropertyMock,
            return_value=test_payload
        ):
            # Get the public repos URL
            result = client._public_repos_url
            
            # Assert that the result matches the expected URL
            self.assertEqual(
                result,
                "https://api.github.com/orgs/test-org/repos"
            )

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns the expected list of repos."""
        # Test payload for get_json
        test_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None}
        ]
        mock_get_json.return_value = test_payload

        # Create an instance of GithubOrgClient
        client = GithubOrgClient("test-org")

        # Mock the _public_repos_url property
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock,
            return_value="https://api.github.com/orgs/test-org/repos"
        ):
            # Get the public repos
            result = client.public_repos()

            # Assert that get_json was called once with the correct URL
            mock_get_json.assert_called_once_with(
                "https://api.github.com/orgs/test-org/repos"
            )

            # Assert that the result matches the expected list of repo names
            self.assertEqual(
                result,
                ["repo1", "repo2", "repo3"]
            )

    @parameterized.expand([
        (
            {"license": {"key": "my_license"}},
            "my_license",
            True
        ),
        (
            {"license": {"key": "other_license"}},
            "my_license",
            False
        ),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that has_license returns the expected boolean.
        
        Args:
            repo: The repository dictionary to test
            license_key: The license key to check for
            expected: The expected boolean result
        """
        # Create an instance of GithubOrgClient
        client = GithubOrgClient("test-org")
        
        # Test the has_license method
        result = client.has_license(repo, license_key)
        
        # Assert that the result matches the expected value
        self.assertEqual(result, expected)


@parameterized_class([
    {
        'org_payload': TEST_PAYLOAD[0][0],
        'repos_payload': TEST_PAYLOAD[0][1],
        'expected_repos': TEST_PAYLOAD[0][2],
        'apache2_repos': TEST_PAYLOAD[0][3],
    },
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient class.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests."""
        # Start patcher for requests.get
        cls.get_patcher = patch('requests.get')
        
        # Get the mock object
        cls.mock_get = cls.get_patcher.start()
        
        # Set up the side effect function
        def side_effect(url):
            """Return different payloads based on the URL."""
            if url == f"https://api.github.com/orgs/{cls.org_payload['login']}":
                return Mock(json=lambda: cls.org_payload)
            elif url == cls.org_payload['repos_url']:
                return Mock(json=lambda: cls.repos_payload)
            return Mock(json=lambda: {})
        
        # Set the side effect
        cls.mock_get.side_effect = side_effect
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures after running tests."""
        # Stop the patcher
        cls.get_patcher.stop()


if __name__ == '__main__':
    unittest.main() 