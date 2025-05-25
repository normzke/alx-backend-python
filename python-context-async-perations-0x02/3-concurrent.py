import asyncio
import aiosqlite

async def async_fetch_users():
    """
    Asynchronously fetch all users from the database.
    
    Returns:
        list: All users in the database
    """
    print("Starting async_fetch_users...")
    
    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute("SELECT * FROM users")
        users = await cursor.fetchall()
        print(f"async_fetch_users completed: Found {len(users)} total users")
        return users

async def async_fetch_older_users():
    """
    Asynchronously fetch users older than 40 from the database.
    
    Returns:
        list: Users older than 40
    """
    print("Starting async_fetch_older_users...")
    
    async with aiosqlite.connect("users.db") as db:
        cursor = await db.execute("SELECT * FROM users WHERE age > ?", (40,))
        older_users = await cursor.fetchall()
        print(f"async_fetch_older_users completed: Found {len(older_users)} users older than 40")
        return older_users

async def fetch_concurrently():
    """
    Execute both database queries concurrently using asyncio.gather.
    
    Returns:
        tuple: (all_users, older_users) - Results from both queries
    """
    print("=" * 60)
    print("Starting concurrent database queries...")
    print("=" * 60)
    
    # Use asyncio.gather to execute both queries concurrently
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    print("\n" + "=" * 60)
    print("Concurrent queries completed!")
    print("=" * 60)
    
    return all_users, older_users

def display_results(all_users, older_users):
    """
    Display the results from both queries in a formatted way.
    
    Args:
        all_users (list): All users from the database
        older_users (list): Users older than 40
    """
    print("\n📊 QUERY RESULTS")
    print("=" * 60)
    
    # Display all users
    print(f"\n🔍 ALL USERS ({len(all_users)} found):")
    print("-" * 50)
    if all_users:
        for user in all_users:
            print(f"ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Age: {user[3]}")
    else:
        print("No users found in database")
    
    # Display older users
    print(f"\n👴 USERS OLDER THAN 40 ({len(older_users)} found):")
    print("-" * 50)
    if older_users:
        for user in older_users:
            print(f"ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Age: {user[3]}")
    else:
        print("No users older than 40 found")
    
    print("\n" + "=" * 60)

async def main():
    """
    Main async function that orchestrates the concurrent database operations.
    """
    try:
        # Execute concurrent queries
        all_users, older_users = await fetch_concurrently()
        
        # Display results
        display_results(all_users, older_users)
        
        # Performance comparison info
        print("\n⚡ PERFORMANCE BENEFITS:")
        print("- Queries ran concurrently instead of sequentially")
        print("- Total execution time is approximately the time of the slowest query")
        print("- Database connections are handled asynchronously")
        print("- Non-blocking I/O operations improve overall performance")
        
    except Exception as e:
        print(f"❌ Error during concurrent execution: {e}")

if __name__ == "__main__":
    print("🚀 Running concurrent asynchronous database queries...")
    print("📦 Note: Make sure 'aiosqlite' is installed: pip install aiosqlite")
    print()
    
    # Use asyncio.run to execute the concurrent fetch
    asyncio.run(main()) 