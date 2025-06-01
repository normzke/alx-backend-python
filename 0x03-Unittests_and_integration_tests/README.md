# Unit Tests and Integration Tests

This project focuses on implementing unit tests and integration tests in Python using the `unittest` framework. The project demonstrates various testing techniques including:

- Parameterized testing
- Mocking and patching
- Integration testing with fixtures
- Testing exceptions
- Testing decorators

## Files

- `utils.py`: Contains utility functions for testing
- `test_utils.py`: Unit tests for the utility functions
- `test_client.py`: Integration tests for the GithubOrgClient
- `fixtures.py`: Test fixtures for integration tests
- `requirements.txt`: Project dependencies

## Requirements

- Python 3.8+
- parameterized==0.8.1
- requests==2.31.0

## Usage

Run the tests using:

```bash
python -m unittest discover
```

Or run specific test files:

```bash
python -m unittest test_utils.py
python -m unittest test_client.py
``` 