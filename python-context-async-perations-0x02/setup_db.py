import sqlite3

def setup_database():
    """Create a users database with sample data for testing"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER
        )
    ''')
    
    # Insert sample data
    sample_users = [
        ('Alice Johnson', 'alice@email.com', 28),
        ('Bob Smith', 'bob@email.com', 34),
        ('Charlie Brown', 'charlie@email.com', 22),
        ('Diana Prince', 'diana@email.com', 30),
        ('Eve Davis', 'eve@email.com', 26)
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO users (name, email, age) VALUES (?, ?, ?)
    ''', sample_users)
    
    conn.commit()
    conn.close()
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database() 