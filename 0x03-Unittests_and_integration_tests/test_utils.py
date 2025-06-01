#!/usr/bin/env python3
"""Unit tests for utils module.
"""
import unittest
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize
from unittest.mock import patch, Mock


class TestAccessNestedMap(unittest.TestCase):
    """Test cases for access_nested_map function.
    """
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test access_nested_map with valid inputs.
        
        Args:
            nested_map: The nested map to access
            path: The path to the value
            expected: The expected value
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_key):
        """Test access_nested_map with invalid inputs.
        
        Args:
            nested_map: The nested map to access
            path: The path to the value
            expected_key: The key that should be in the KeyError
        """
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), f"'{expected_key}'")


class TestGetJson(unittest.TestCase):
    """Test cases for get_json function.
    """
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('requests.get')
    def test_get_json(self, test_url, test_payload, mock_get):
        """Test get_json function with mocked requests.get.
        
        Args:
            test_url: The URL to test with
            test_payload: The expected JSON payload
            mock_get: The mocked requests.get function
        """
        # Create a mock response object with a json method
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response
        
        # Call the function
        result = get_json(test_url)
        
        # Assert that requests.get was called exactly once with test_url
        mock_get.assert_called_once_with(test_url)
        
        # Assert that the result matches test_payload
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test cases for memoize decorator.
    """
    def test_memoize(self):
        """Test that memoize decorator caches the result."""
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        # Create an instance of TestClass
        test_instance = TestClass()
        
        # Patch a_method to track calls
        with patch.object(TestClass, 'a_method') as mock_method:
            # Set the return value for the mock
            mock_method.return_value = 42
            
            # Call a_property twice
            result1 = test_instance.a_property
            result2 = test_instance.a_property
            
            # Assert that a_method was called only once
            mock_method.assert_called_once()
            
            # Assert that both results are correct
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)


if __name__ == '__main__':
    unittest.main()
