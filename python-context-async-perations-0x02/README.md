# Python Context Managers and Async Operations

This project demonstrates advanced Python concepts including context managers and asynchronous programming with database operations.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up the database:
```bash
python setup_db.py
```

## Tasks

### Task 0: Custom Class-Based Context Manager (`0-databaseconnection.py`)
- Implements `DatabaseConnection` class with `__enter__` and `__exit__` methods
- Automatically handles database connection lifecycle
- Demonstrates basic context manager usage

### Task 1: Reusable Query Context Manager (`1-execute.py`)
- Implements `ExecuteQuery` class for query execution and connection management
- Takes query and parameters as input
- Returns query results directly from context manager
- Example: `SELECT * FROM users WHERE age > ?` with parameter `25`

### Task 2: Concurrent Asynchronous Queries (`3-concurrent.py`)
- Uses `aiosqlite` for asynchronous database operations
- Implements two async functions:
  - `async_fetch_users()` - fetches all users
  - `async_fetch_older_users()` - fetches users older than 40
- Uses `asyncio.gather()` for concurrent execution
- Demonstrates performance benefits of async operations

## Running the Tasks

```bash
# Task 0: Basic context manager
python 0-databaseconnection.py

# Task 1: Reusable query context manager
python 1-execute.py

# Task 2: Concurrent async queries
python 3-concurrent.py
```

## Key Concepts Demonstrated

- **Context Managers**: Automatic resource management
- **Async Programming**: Non-blocking I/O operations
- **Concurrent Execution**: Multiple operations running simultaneously
- **Database Operations**: SQLite integration with proper connection handling
- **Error Handling**: Robust exception management and rollback mechanisms 