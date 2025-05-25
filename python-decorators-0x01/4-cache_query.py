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

query_cache = {}

def cache_query(func):
    """
    Decorator that caches the results of database queries to avoid redundant calls.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The decorated function that uses cached results when available
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from function arguments
        query = None
        
        # Check if 'query' is in kwargs
        if 'query' in kwargs:
            query = kwargs['query']
        else:
            # Look for query in args (should be the second argument after conn)
            # Since we're decorating after @with_db_connection, 
            # the original function signature is func(conn, query), 
            # but when called it becomes func(query) due to connection injection
            if len(args) >= 2:
                query = args[1]  # conn is args[0], query is args[1]
        
        # Create a cache key from the query
        cache_key = query
        
        # Check if result is already cached
        if cache_key and cache_key in query_cache:
            print(f"Cache hit! Returning cached result for query: {query}")
            return query_cache[cache_key]
        
        # Execute the function if not cached
        print(f"Cache miss! Executing query: {query}")
        result = func(*args, **kwargs)
        
        # Cache the result if we have a valid query
        if cache_key:
            query_cache[cache_key] = result
            print(f"Result cached for query: {query}")
        
        return result
    
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")
print(f"First call result: {len(users) if users else 0} users found")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print(f"Second call result: {len(users_again) if users_again else 0} users found")

#### Different query will not use cache
specific_user = fetch_users_with_cache(query="SELECT * FROM users WHERE id = 1")
print(f"Different query result: {len(specific_user) if specific_user else 0} users found") 