import sqlite3

DB_PATH = 'game_data.db'

def get_all_users():
    """Retrieve all users from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    
    # Return users as a list of dictionaries
    return [
        {'id': user[0], 'username': user[1], 'level': user[3], 'coins': user[4]}
        for user in users
    ]

def get_user_by_username(username):
    """Retrieve a user by their username."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            'id': user[0],
            'username': user[1],
            'level': user[3],
            'coins': user[4]
        }
    else:
        print(f"User {username} not found.")
        return None

def update_user_level(username, new_level):
    """Update the level of a user by their username."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET level = ? WHERE username = ?', (new_level, username))
    conn.commit()
    conn.close()

    print(f"Updated {username}'s level to {new_level}.")

def update_user_coins(username, new_coins):
    """Update the coin count of a user by their username."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET coins = ? WHERE username = ?', (new_coins, username))
    conn.commit()
    conn.close()

    print(f"Updated {username}'s coins to {new_coins}.")

def delete_user(username):
    """Delete a user from the database by their username."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    conn.commit()
    conn.close()

    print(f"Deleted user {username} from the database.")

def print_all_tables():
    """Print all table names in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query to get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()

    if tables:
        print("Tables in the database:")
        for table in tables:
            print(table[0])
    else:
        print("No tables found in the database.")

def print_table_schema(table_name):
    """Print the schema of a particular table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query to get the schema of the table
    cursor.execute(f"PRAGMA table_info({table_name});")
    schema = cursor.fetchall()
    conn.close()

    if schema:
        print(f"Schema of table '{table_name}':")
        for column in schema:
            print(f"Column: {column[1]}, Type: {column[2]}, Not Null: {column[3]}, Default: {column[4]}")
    else:
        print(f"Table '{table_name}' not found or empty.")


# Example usage
if __name__ == "__main__":
    print_all_tables()

    # # Fetch all users
    # users = get_all_users()
    # print("All Users:")
    # for user in users:
    #     print(user)

    # # Fetch a user by username
    # user_data = get_user_by_username("player1")
    # if user_data:
    #     print(f"\nUser Data for 'player1': {user_data}")

    # # Update a user's level
    # update_user_level("player1", 5)

    # # Update a user's coins
    # update_user_coins("player1", 100)

    # # Delete a user
    # delete_user("player2")
