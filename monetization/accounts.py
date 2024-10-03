# accounts.py
import sqlite3
import hashlib

DB_PATH = 'game_data.db'

def initialize_database():
    """Initialize the SQLite database and create the users table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create a table for users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            coins INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    password_hash = hash_password(password)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        conn.close()
        print("Registration successful!")
        return True
    except sqlite3.IntegrityError:
        print("Username already exists. Please choose a different username.")
        return False

def login_user(username, password):
    password_hash = hash_password(password)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password_hash))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        print("Login successful!")
        # Return user data as a dictionary for easy access
        return {
            'id': user[0],
            'username': user[1],
            'level': user[3],
            'coins': user[4]
        }
    else:
        print("Invalid username or password.")
        return None

# Initialize the database when this module is imported
initialize_database()
