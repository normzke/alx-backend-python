import sqlite3

class DatabaseConnection:
    """
    A class-based context manager for handling database connections.
    
    This context manager automatically opens a database connection when entering
    the context and ensures the connection is properly closed when exiting,
    even if an exception occurs.
    """
    
    def __init__(self, db_name):
        """
        Initialize the DatabaseConnection context manager.
        
        Args:
            db_name (str): The name/path of the database file
        """
        self.db_name = db_name
        self.connection = None
    
    def __enter__(self):
        """
        Enter the context manager - opens the database connection.
        
        Returns:
            sqlite3.Connection: The database connection object
        """
        print(f"Opening database connection to {self.db_name}")
        self.connection = sqlite3.connect(self.db_name)
        return self.connection
    
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

# Usage example with the context manager
if __name__ == "__main__":
    # Use the context manager with the with statement
    with DatabaseConnection("users.db") as conn:
        cursor = conn.cursor()
        
        # Perform the query SELECT * FROM users
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        
        # Print the results from the query
        print("\nQuery results:")
        print("=" * 50)
        if results:
            print(f"Found {len(results)} users:")
            for row in results:
                print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Age: {row[3]}")
        else:
            print("No users found in the database.")
        print("=" * 50)
    
    print("\nContext manager has automatically closed the connection.") 