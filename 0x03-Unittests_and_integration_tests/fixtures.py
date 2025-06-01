#!/usr/bin/env python3
"""Test fixtures for GithubOrgClient tests.
"""
import json
from typing import Dict, List, Tuple

# Test payload for organization
org_payload = {
    "login": "test-org",
    "id": 123456,
    "repos_url": "https://api.github.com/orgs/test-org/repos"
}

# Test payload for repositories
repos_payload = [
    {
        "name": "repo1",
        "license": {"key": "mit"}
    },
    {
        "name": "repo2",
        "license": {"key": "apache-2.0"}
    },
    {
        "name": "repo3",
        "license": None
    }
]

# Expected list of repository names
expected_repos = ["repo1", "repo2", "repo3"]

# Expected list of Apache 2.0 licensed repositories
apache2_repos = ["repo2"]

# Combined test payload
TEST_PAYLOAD = [
    (org_payload, repos_payload, expected_repos, apache2_repos)
] 