from database_manager import DatabaseManager
import os

# Initialize DatabaseManager with the correct mode (this can be passed as a parameter or set globally)
db_mode = os.getenv('DB_MODE', 'postgres')
database_manager = DatabaseManager(db_mode=db_mode)

def register_user(username, password):
    return database_manager.register_user(username, password)

def login_user(username, password):
    return database_manager.login_user(username, password)


# import sqlite3
# import psycopg2
# import hashlib
# import os

# # SQLite DB for session data
# DB_PATH = 'session_data.db'

# # PostgreSQL configuration
# POSTGRES_DB = {
#     'dbname': 'adventure_game',
#     'user': 'adventure_game',
#     'password': 'adventure_game',
#     'host': 'localhost',
#     'port': 5432
# }

# def initialize_local_session_db():
#     """Initialize the SQLite database to store session data locally."""
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     # Create a table for session data (not users)
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS session (
#             session_token TEXT PRIMARY KEY,
#             user_id INTEGER,
#             last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     ''')
    
#     conn.commit()
#     conn.close()

# def get_postgres_connection():
#     """Helper function to connect to PostgreSQL."""
#     return psycopg2.connect(**POSTGRES_DB)

# def hash_password(password):
#     """Hash the password using SHA-256."""
#     return hashlib.sha256(password.encode()).hexdigest()

# def register_user(username, password):
#     """Register a new user in the PostgreSQL database."""
#     password_hash = hash_password(password)

#     try:
#         conn = get_postgres_connection()
#         cursor = conn.cursor()
#         cursor.execute('''
#             INSERT INTO users (username, password_hash, level, coins) 
#             VALUES (%s, %s, %s, %s)
#         ''', (username, password_hash, 1, 0))  # Default level = 1, coins = 0
#         conn.commit()
#         cursor.close()
#         conn.close()
#         print("Registration successful!")
#         return True
#     except psycopg2.IntegrityError:
#         print("Username already exists. Please choose a different username.")
#         return False

# def login_user(username, password):
#     """Authenticate a user against the PostgreSQL database."""
#     password_hash = hash_password(password)

#     conn = get_postgres_connection()
#     cursor = conn.cursor()
#     cursor.execute('''
#         SELECT id, username, level, coins 
#         FROM users 
#         WHERE username = %s AND password_hash = %s
#     ''', (username, password_hash))
#     user = cursor.fetchone()
#     cursor.close()
#     conn.close()

#     if user:
#         print("Login successful!")
#         session_token = create_session(user[0])  # Store user ID in local session
#         return {
#             'id': user[0],
#             'username': user[1],
#             'level': user[2],
#             'coins': user[3],
#             'session_token': session_token  # Include session token in the response
#         }
#     else:
#         print("Invalid username or password.")
#         return None

# def create_session(user_id):
#     """Create a session entry in the local SQLite database for the logged-in user."""
#     session_token = hashlib.sha256(os.urandom(16)).hexdigest()  # Generate a random session token
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
    
#     # Store session data (user_id and session token)
#     cursor.execute('''
#         INSERT INTO session (session_token, user_id) 
#         VALUES (?, ?)
#     ''', (session_token, user_id))
#     conn.commit()
#     conn.close()

#     return session_token

# def get_user_by_session(session_token):
#     """Retrieve user info based on session token from local SQLite."""
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute('SELECT user_id FROM session WHERE session_token = ?', (session_token,))
#     session_data = cursor.fetchone()
#     conn.close()

#     if session_data:
#         user_id = session_data[0]
        
#         # Fetch user details from PostgreSQL using user_id
#         conn = get_postgres_connection()
#         cursor = conn.cursor()
#         cursor.execute('SELECT id, username, level, coins FROM users WHERE id = %s', (user_id,))
#         user = cursor.fetchone()
#         cursor.close()
#         conn.close()

#         if user:
#             return {
#                 'id': user[0],
#                 'username': user[1],
#                 'level': user[2],
#                 'coins': user[3]
#             }
#     return None

# def logout_user(session_token):
#     """Remove the session from local SQLite to log the user out."""
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute('DELETE FROM session WHERE session_token = ?', (session_token,))
#     conn.commit()
#     conn.close()
#     print("User logged out.")

# # Initialize the local session database when the module is imported
# initialize_local_session_db()
