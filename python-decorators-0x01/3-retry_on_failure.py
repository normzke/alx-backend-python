import time
import sqlite3 
import functools

def with_db_connection(func):
    """
    Decorator that automatically handles opening and closing database connections.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The decorated function that receives a database connection as first parameter
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect('users.db')
        try:
            # Call the original function with connection as first argument
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Always close the connection, even if an exception occurs
            conn.close()
    
    return wrapper

def retry_on_failure(retries=3, delay=2):
    """
    Decorator that retries database operations if they fail due to transient errors.
    
    Args:
        retries: Number of retry attempts (default: 3)
        delay: Delay in seconds between retry attempts (default: 2)
        
    Returns:
        A decorator function that wraps the target function with retry logic
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(retries + 1):  # +1 for the initial attempt
                try:
                    # Try to execute the function
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    last_exception = e
                    
                    # If this was the last attempt, re-raise the exception
                    if attempt == retries:
                        print(f"Function {func.__name__} failed after {retries + 1} attempts")
                        raise last_exception
                    
                    # Log the retry attempt
                    print(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")
                    print(f"Retrying in {delay} seconds... (Attempt {attempt + 2}/{retries + 1})")
                    
                    # Wait before retrying
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure
users = fetch_users_with_retry()
print(users) 