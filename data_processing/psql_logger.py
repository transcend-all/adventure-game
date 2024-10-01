# psql_logger.py
import psycopg2

class PSQLLogger:
    def __init__(self, db_config):
        """Initialize the PostgreSQL logger with connection details."""
        self.connection = psycopg2.connect(
            dbname=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            port=db_config['port']
        )
        self.cursor = self.connection.cursor()

        # Create the table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_movements (
                id SERIAL PRIMARY KEY,
                timestamp BIGINT,
                event_type VARCHAR(50),
                player_position VARCHAR(50)
            )
        ''')
        self.connection.commit()

    def log_event(self, event_type, event_data):
        """Log the event to the PostgreSQL database."""
        query = '''
            INSERT INTO player_movements (timestamp, event_type, player_position)
            VALUES (%s, %s, %s)
        '''
        self.cursor.execute(query, (int(event_data['timestamp']), event_type, str(event_data['player_position'])))
        self.connection.commit()

    def close(self):
        """Close the connection to the database."""
        self.cursor.close()
        self.connection.close()
