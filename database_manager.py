import boto3
import psycopg2
import sqlite3
import hashlib
import os
import logging
from botocore.exceptions import ClientError
from psycopg2 import sql
from dataclasses import dataclass

try:
    import databricks.sql as dbsql
except ImportError:
    dbsql = None
    logging.warning("Databricks SQL connector not installed. Databricks mode will be unavailable.")


# PostgreSQL configuration
POSTGRES_DB = {
    'dbname': 'adventure_game',
    'user': 'adventure_game',
    'password': 'adventure_game',
    'host': 'localhost',
    'port': 5432
}

# SQLite DB for session data
DB_PATH = 'session_data.db'

SQLITE_DB_PATH = 'session_data.db'

# DynamoDB Table Name
DYNAMODB_USERS_TABLE = 'adventure_game_users'
DYNAMODB_SESSIONS_TABLE = 'adventure_game_sessions'


class DatabaseManager:
    def __init__(self, db_mode='postgres'):
        self.db_mode = db_mode
        self.conn = None
        if db_mode == 'dynamodb':
            # Set up DynamoDB client
            self.dynamodb = boto3.resource('dynamodb')
            self.table = self.dynamodb.Table('adventure_game_users')
        elif db_mode == 'postgres':
            self.initialize_postgres()

    def get_postgres_connection(self):
        """Helper function to connect to PostgreSQL."""
        if self.conn is None:
            self.conn = psycopg2.connect(**POSTGRES_DB)
        return self.conn
    
    def initialize_postgres(self):
        """Ensure that the users table exists in the PostgreSQL database."""
        conn = self.get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                level INT DEFAULT 1,
                coins INT DEFAULT 0,
                health_potions INT DEFAULT 0,
                attack_boosts INT DEFAULT 0,
                defense_boosts INT DEFAULT 0
            );
        ''')
        conn.commit()
        cursor.close()
        print("Checked for or created users table in PostgreSQL.")

    def close_postgres_connection(self):
        """Close the PostgreSQL connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def hash_password(self, password):
        """Hash the password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password):
        """Register a new user in the chosen database."""
        password_hash = self.hash_password(password)

        if self.db_mode == 'postgres':
            return self._register_user_postgres(username, password_hash)
        elif self.db_mode == 'dynamodb':
            return self._register_user_dynamodb(username, password_hash)

    def _register_user_postgres(self, username, password_hash):
        """Register a new user in PostgreSQL."""
        try:
            conn = self.get_postgres_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password_hash, level, coins, health_potions, attack_boosts, defense_boosts) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (username, password_hash, 1, 0, 0, 0, 0))  # Default level = 1, coins = 0
            conn.commit()
            cursor.close()
            print("Registration successful in PostgreSQL!")
            return True
        except psycopg2.IntegrityError:
            print("Username already exists. Please choose a different username.")
            return False

    def _register_user_dynamodb(self, username, password_hash):
        """Register a new user in DynamoDB."""
        try:
            self.table.put_item(
                Item={
                    'username': username,
                    'password_hash': password_hash,
                    'level': 1,
                    'coins': 0
                },
                ConditionExpression="attribute_not_exists(username)"  # Ensure uniqueness
            )
            print("Registration successful in DynamoDB!")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print("Username already exists in DynamoDB.")
                return False
            else:
                raise

    def login_user(self, username, password):
        """Authenticate a user from the chosen database."""
        password_hash = self.hash_password(password)

        if self.db_mode == 'postgres':
            return self._login_user_postgres(username, password_hash)
        elif self.db_mode == 'dynamodb':
            return self._login_user_dynamodb(username, password_hash)

    def _login_user_postgres(self, username, password_hash):
        """Authenticate a user in PostgreSQL."""
        conn = self.get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, level, coins, health_potions, attack_boosts, defense_boosts
            FROM users 
            WHERE username = %s AND password_hash = %s
        ''', (username, password_hash))
        user = cursor.fetchone()
        cursor.close()

        if user:
            print("Login successful in PostgreSQL!")
            return {
                'id': user[0],
                'username': user[1],
                'level': user[2],
                'coins': user[3]
            }
        else:
            print("Invalid username or password.")
            return None

    def _login_user_dynamodb(self, username, password_hash):
        """Authenticate a user in DynamoDB."""
        try:
            response = self.table.get_item(Key={'username': username})
            if 'Item' in response and response['Item']['password_hash'] == password_hash:
                user = response['Item']
                print("Login successful in DynamoDB!")
                return {
                    'username': user['username'],
                    'level': user['level'],
                    'coins': user['coins']
                }
            else:
                print("Invalid username or password in DynamoDB.")
                return None
        except ClientError as e:
            logging.error(f"Failed to login with DynamoDB: {e}")
            return None

    def save_progress(self, username, level, coins, health_potions, attack_boosts, defense_boosts):
        if self.db_mode == 'postgres':
            # Handle saving progress to PostgreSQL
            self.save_to_postgres(username, level, coins, health_potions, attack_boosts, defense_boosts)
        elif self.db_mode == 'dynamodb':
            # Handle saving progress to DynamoDB
            self.save_to_dynamodb(username, level, coins, health_potions, attack_boosts, defense_boosts)

    def save_to_postgres(self, username, level, coins, health_potions, attack_boosts, defense_boosts):
        try:
            conn = self.get_postgres_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET level = %s, coins = %s, health_potions = %s, attack_boosts = %s, defense_boosts = %s WHERE username = %s',
                           (level, coins, health_potions, attack_boosts, defense_boosts, username))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Saving progress: username={username}, level={level}, coins={coins}, health_potions={health_potions}, attack_boosts={attack_boosts}, defense_boosts={defense_boosts}")
            print(f"Progress saved to Postgres for {username}.")
        except Exception as e:
            logging.error(f"Failed to save progress to Postgres: {e}")
            print("Error saving progress to Postgres.")

    def save_to_dynamodb(self, username, level, coins, health_potions, attack_boosts, defense_boosts):
        try:
            # DynamoDB save operation
            response = self.table.put_item(
                Item={
                    'username': username,
                    'level': level,
                    'coins': coins,
                    'health_potions': health_potions,
                    'attack_boosts': attack_boosts,
                    'defense_boosts': defense_boosts
                }
            )
            logging.info(f"Progress saved to DynamoDB for {username}: {response}")
            print(f"Progress saved to DynamoDB for {username}.")
        except Exception as e:
            logging.error(f"Failed to save progress to DynamoDB: {e}")
            print("Error saving progress to DynamoDB.")

    def get_user_items_postgres(self, username):
        """Fetch the user's item counts from PostgreSQL."""
        try:
            conn = self.get_postgres_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT health_potions, attack_boosts, defense_boosts
                FROM users
                WHERE username = %s
            ''', (username,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                return {
                    'health_potions': result[0],
                    'attack_boosts': result[1],
                    'defense_boosts': result[2]
                }
            else:
                print("User not found.")
                return None
        except Exception as e:
            logging.error(f"Error fetching user items: {e}")
            return None

    def get_user_items_dynamodb(self, username):
        """Fetch the user's item counts from DynamoDB."""
        try:
            response = self.table.get_item(Key={'username': username})
            if 'Item' in response:
                return {
                    'health_potions': response['Item'].get('health_potions', 0),
                    'attack_boosts': response['Item'].get('attack_boosts', 0),
                    'defense_boosts': response['Item'].get('defense_boosts', 0)
                }
            else:
                print("User not found in DynamoDB.")
                return None
        except Exception as e:
            logging.error(f"Error fetching user items from DynamoDB: {e}")
            return None

    def get_user_items(self, username):
        """Fetch the user's item counts based on db_mode."""
        if self.db_mode == 'postgres':
            return self.get_user_items_postgres(username)
        elif self.db_mode == 'dynamodb':
            return self.get_user_items_dynamodb(username)
        else:
            print("Unsupported database mode.")
            return None
        
    def increment_item(self, username, item_type, amount=1):
        """General method to increment item count based on db_mode."""
        if self.db_mode == 'postgres':
            self.increment_item_postgres(username, item_type, amount)
        elif self.db_mode == 'dynamodb':
            self.increment_item_dynamodb(username, item_type, amount)
        else:
            print("Unsupported database mode.")

    def decrement_item(self, username, item_type, amount=1):
        """General method to decrement item count based on db_mode."""
        if self.db_mode == 'postgres':
            self.decrement_item_postgres(username, item_type, amount)
        elif self.db_mode == 'dynamodb':
            self.decrement_item_dynamodb(username, item_type, amount)
        else:
            print("Unsupported database mode.")