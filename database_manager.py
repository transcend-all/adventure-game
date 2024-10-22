import boto3
import psycopg2
import sqlite3
import hashlib
import os
import logging
from botocore.exceptions import ClientError
from psycopg2 import sql
from dataclasses import dataclass
from characters.player import Player
from datetime import datetime

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
        self.postgres_conn = None
        if db_mode == 'postgres':
            self.db_config = {
                'dbname': 'adventure_game',
                'user': 'adventure_game',
                'password': 'adventure_game',
                'host': 'localhost',
                'port': 5432
            }
            self.ensure_tables_exist()

    def get_postgres_connection(self):
        if not self.postgres_conn or self.postgres_conn.closed:
            try:
                self.postgres_conn = psycopg2.connect(**self.db_config)
                return self.postgres_conn
            except (Exception, psycopg2.Error) as error:
                print(f"Error while connecting to PostgreSQL: {error}")
                return None
        return self.postgres_conn
    
    def ensure_tables_exist(self):
        conn = self.get_postgres_connection()
        if conn is None:
            print("Failed to establish database connection")
            return
        
        try:
            with conn.cursor() as cursor:
                # Create users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        coins INTEGER DEFAULT 0
                    )
                """)
                
                # Create payment_cards table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS payment_cards (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        card_number TEXT,
                        expiration_date TEXT,
                        cvv TEXT,
                        cardholder_name TEXT
                    )
                """)
                
                # Create sessions table with additional columns
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        end_time TIMESTAMP,
                        duration INTERVAL,
                        start_level INTEGER,
                        end_level INTEGER,
                        enemies_killed INTEGER DEFAULT 0,
                        coins_collected INTEGER DEFAULT 0,
                        items_purchased TEXT[],
                        items_used TEXT[],
                        credit_card_added BOOLEAN DEFAULT FALSE
                    )
                """)
                
                conn.commit()
                print("Tables created successfully (if they didn't exist)")
        except (Exception, psycopg2.Error) as error:
            print(f"Error creating tables: {error}")
        finally:
            if conn:
                conn.close()

    def close_postgres_connection(self):
        """Close the PostgreSQL connection."""
        if self.postgres_conn:
            self.postgres_conn.close()
            print("PostgreSQL connection is closed")

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
            if conn is None:
                print("Failed to establish database connection")
                return False
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password_hash, level, coins) 
                VALUES (%s, %s, %s, %s)
            ''', (username, password_hash, 1, 0))  # Default level = 1, coins = 0
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

    def _login_user_postgres(self, username, password):
        """Authenticate a user in PostgreSQL."""
        conn = self.get_postgres_connection()
        if conn is None:
            print("Failed to establish database connection")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, level, coins 
                FROM users 
                WHERE username = %s AND password_hash = %s
            """, (username, password))
            user = cursor.fetchone()
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'level': user[2],
                    'coins': user[3]
                }
            print(user)
            return None
        except Exception as e:
            print(f"Error during login: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

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
            if conn is None:
                print("Failed to establish database connection")
                return
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
            if conn is None:
                print("Failed to establish database connection")
                return None
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

    def save_card_info(self, user_id, card_info):
        print(f"Attempting to save card info for user_id: {user_id}")  # Debug print
        if user_id is None:
            print("Error: user_id is None")
            return False
        if self.db_mode == 'postgres':
            conn = self.get_postgres_connection()
            if conn is None:
                print("Failed to establish database connection")
                return False
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO payment_cards (user_id, card_number, expiration_date, cvv, cardholder_name) 
                    VALUES (%s, %s, %s, %s, %s)
                ''', (user_id, card_info['card_number'], card_info['expiration_date'], card_info['cvv'], card_info['cardholder_name']))
                conn.commit()
                cursor.close()
                print(f"Credit card information saved successfully for user_id: {user_id}")
                return True
            except (Exception, psycopg2.Error) as error:
                print(f"Error saving credit card information: {error}")
                return False
            finally:
                if conn:
                    conn.close()
        elif self.db_mode == 'dynamodb':
            # DynamoDB implementation
            pass

    def create_user(self, username, password):
        conn = self.get_postgres_connection()
        if conn is None:
            return None
        try:
            cursor = conn.cursor()
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (username, password_hash)
                VALUES (%s, %s)
                RETURNING id, username, coins
            """, (username, password_hash))
            user = cursor.fetchone()
            conn.commit()
            return Player(name=user[1], currency=user[2], id=user[0])
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def start_session(self, user_id, start_level):
        if self.db_mode == 'postgres':
            return self._start_session_postgres(user_id, start_level)
        elif self.db_mode == 'dynamodb':
            return self._start_session_dynamodb(user_id, start_level)

    def _start_session_postgres(self, user_id, start_level):
        conn = self.get_postgres_connection()
        if conn is None:
            print("Failed to establish database connection")
            return None
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO sessions (user_id, start_time, start_level)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (user_id, datetime.now(), start_level))
                session_id = cursor.fetchone()[0]
                conn.commit()
                print(f"Session started for user {user_id}, session ID: {session_id}")
                return session_id
        except (Exception, psycopg2.Error) as error:
            print(f"Error starting session: {error}")
            return None
        finally:
            if conn:
                conn.close()

    def _start_session_dynamodb(self, user_id, start_level):
        # Implement DynamoDB session start logic here
        pass

    def end_session(self, session_id, end_level, enemies_killed_increment=0, coins_collected_increment=0, new_item_purchased=None, new_item_used=None):
        if self.db_mode == 'postgres':
            return self._end_session_postgres(session_id, end_level, enemies_killed_increment, coins_collected_increment, new_item_purchased, new_item_used)
        elif self.db_mode == 'dynamodb':
            return self._end_session_dynamodb(session_id, end_level, enemies_killed_increment, coins_collected_increment, new_item_purchased, new_item_used)

    def _end_session_postgres(self, session_id, end_level, enemies_killed_increment=0, coins_collected_increment=0, new_item_purchased=None, new_item_used=None):
        conn = self.get_postgres_connection()
        if conn is None:
            print("Failed to establish database connection")
            return False
        
        try:
            with conn.cursor() as cursor:
                end_time = datetime.now()
                cursor.execute("""
                    UPDATE sessions
                    SET end_time = %s,
                        duration = %s - start_time,
                        end_level = %s,
                        enemies_killed = enemies_killed + %s,
                        coins_collected = coins_collected + %s,
                        items_purchased = CASE WHEN %s IS NOT NULL THEN array_append(items_purchased, %s) ELSE items_purchased END,
                        items_used = CASE WHEN %s IS NOT NULL THEN array_append(items_used, %s) ELSE items_used END
                    WHERE id = %s
                """, (
                        end_time,  # 1. end_time
                        end_time,  # 2. duration calculation
                        end_level,  # 3. end_level
                        enemies_killed_increment,  # 4. enemies_killed increment
                        coins_collected_increment,  # 5. coins_collected increment
                        new_item_purchased,  # 6. items_purchased condition
                        new_item_purchased,  # 7. items_purchased value
                        new_item_used,  # 8. items_used condition
                        new_item_used,  # 9. items_used value
                        session_id  # 10. WHERE id
                    ))
                conn.commit()
                print(f"Session {session_id} ended successfully in database")
                return True
        except (Exception, psycopg2.Error) as error:
            print(f"Error ending session: {error}")
            return False
        finally:
            if conn:
                conn.close()

    def _end_session_dynamodb(self, session_id, end_level):
        # Implement DynamoDB session end logic here
        pass

    def update_session_data(self, session_id, enemies_killed=0, coins_collected=0, item_purchased=None, item_used=None):
        if self.db_mode == 'postgres':
            return self._update_session_data_postgres(session_id, enemies_killed, coins_collected, item_purchased, item_used)
        elif self.db_mode == 'dynamodb':
            return self._update_session_data_dynamodb(session_id, enemies_killed, coins_collected, item_purchased, item_used)

    def _update_session_data_postgres(self, session_id, enemies_killed=0, coins_collected=0, item_purchased=None, item_used=None):
        conn = self.get_postgres_connection()
        if conn is None:
            print("Failed to establish database connection")
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE sessions
                    SET enemies_killed = enemies_killed + %s,
                        coins_collected = coins_collected + %s,
                        items_purchased = CASE WHEN %s IS NOT NULL THEN array_append(items_purchased, %s) ELSE items_purchased END,
                        items_used = CASE WHEN %s IS NOT NULL THEN array_append(items_used, %s) ELSE items_used END
                    WHERE id = %s
                """, (enemies_killed, coins_collected, item_purchased, item_purchased, item_used, item_used, session_id))
                conn.commit()
                print(f"Session {session_id} data updated")
                return True
        except (Exception, psycopg2.Error) as error:
            print(f"Error updating session data: {error}")
            return False
        finally:
            if conn:
                conn.close()

    def _update_session_data_dynamodb(self, session_id, enemies_killed=0, coins_collected=0, item_purchased=None, item_used=None):
        # Implement DynamoDB session data update logic here
        pass

    def add_credit_card_to_session(self, session_id):
        if self.db_mode == 'postgres':
            return self._add_credit_card_to_session_postgres(session_id)
        elif self.db_mode == 'dynamodb':
            return self._add_credit_card_to_session_dynamodb(session_id)

    def _add_credit_card_to_session_postgres(self, session_id):
        conn = self.get_postgres_connection()
        if conn is None:
            print("Failed to establish database connection")
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE sessions
                    SET credit_card_added = TRUE
                    WHERE id = %s
                """, (session_id,))
                conn.commit()
                print(f"Credit card added to session {session_id}")
                return True
        except (Exception, psycopg2.Error) as error:
            print(f"Error adding credit card to session: {error}")
            return False
        finally:
            if conn:
                conn.close()

    def _add_credit_card_to_session_dynamodb(self, session_id):
        # Implement DynamoDB credit card addition logic here
        pass

