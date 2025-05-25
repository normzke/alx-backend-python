import sqlite3

class ExecuteQuery:
    """
    A reusable class-based context manager for executing database queries.
    
    This context manager handles both database connection management and query execution.
    It takes a query and parameters as input, executes the query, and returns the results.
    """
    
    def __init__(self, db_name, query, params=None):
        """
        Initialize the ExecuteQuery context manager.
        
        Args:
            db_name (str): The name/path of the database file
            query (str): The SQL query to execute
            params (tuple or list, optional): Parameters for the query
        """
        self.db_name = db_name
        self.query = query
        self.params = params or ()
        self.connection = None
        self.results = None
    
    def __enter__(self):
        """
        Enter the context manager - opens connection, executes query, and returns results.
        
        Returns:
            list: The query results (fetchall() output)
        """
        print(f"Opening database connection to {self.db_name}")
        self.connection = sqlite3.connect(self.db_name)
        
        try:
            cursor = self.connection.cursor()
            print(f"Executing query: {self.query}")
            if self.params:
                print(f"With parameters: {self.params}")
                cursor.execute(self.query, self.params)
            else:
                cursor.execute(self.query)
            
            self.results = cursor.fetchall()
            print(f"Query executed successfully. Found {len(self.results)} rows.")
            return self.results
            
        except Exception as e:
            print(f"Error executing query: {e}")
            if self.connection:
                self.connection.rollback()
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager - closes the database connection.
        
        Args:
            exc_type: The exception type (if an exception occurred)
            exc_val: The exception value (if an exception occurred)
            exc_tb: The exception traceback (if an exception occurred)
            
        Returns:
            None: Returning None means any exception will be propagated
        """
        if self.connection:
            if exc_type is not None:
                print(f"An exception occurred: {exc_type.__name__}: {exc_val}")
                print("Rolling back any pending transactions")
                self.connection.rollback()
            else:
                print("Committing any pending transactions")
                self.connection.commit()
            
            print(f"Closing database connection to {self.db_name}")
            self.connection.close()
            self.connection = None

# Usage example with the specified query and parameter
if __name__ == "__main__":
    # Use the ExecuteQuery context manager with the specific query and parameter
    query = "SELECT * FROM users WHERE age > ?"
    age_threshold = 25
    
    print("=" * 60)
    print("Using ExecuteQuery Context Manager")
    print("=" * 60)
    
    with ExecuteQuery("users.db", query, (age_threshold,)) as results:
        print(f"\nResults for users older than {age_threshold}:")
        print("-" * 50)
        
        if results:
            print(f"Found {len(results)} users:")
            for row in results:
                print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Age: {row[3]}")
        else:
            print(f"No users found with age > {age_threshold}")
        
        print("-" * 50)
    
    print("\nContext manager has automatically handled connection and query execution.")
    
    # Additional example with a different query
    print("\n" + "=" * 60)
    print("Another example: Get all users")
    print("=" * 60)
    
    with ExecuteQuery("users.db", "SELECT * FROM users") as all_users:
        print(f"\nAll users in database:")
        print("-" * 50)
        
        if all_users:
            print(f"Total users: {len(all_users)}")
            for row in all_users:
                print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Age: {row[3]}")
        else:
            print("No users found in the database")
        
        print("-" * 50)
    
    print("\nAll queries completed successfully!") 