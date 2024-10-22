from database_manager import DatabaseManager
import psycopg2
from psycopg2 import sql

class CreditCardInfo:
    def __init__(self, database_manager):
        self.db_manager = database_manager

    def create_table(self):
        if self.db_manager.db_mode == 'postgres':
            conn = None
            try:
                conn = self.db_manager.get_postgres_connection()
                cursor = conn.cursor()
                
                # Check if the table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'payment_cards'
                    );
                """)
                table_exists = cursor.fetchone()[0]
                
                if not table_exists:
                    cursor.execute("""
                        CREATE TABLE payment_cards (
                            id SERIAL PRIMARY KEY,
                            name TEXT,
                            card_number TEXT,
                            expiration_date TEXT,
                            cvv TEXT,
                            cardholder_name TEXT
                        )
                    """)
                    conn.commit()
                    print("Table 'payment_cards' created successfully.")
                else:
                    print("Table 'payment_cards' already exists.")
                
            except (Exception, psycopg2.Error) as error:
                print(f"Error while creating table: {error}")
            finally:
                if conn:
                    cursor.close()
                    conn.close()
        elif self.db_manager.db_mode == 'dynamodb':
            try:
                self.db_manager.dynamodb.create_table(
                    TableName='payment_cards',
                    KeySchema=[
                        {
                            'AttributeName': 'name',
                            'KeyType': 'HASH'  # Partition key
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'name',
                            'AttributeType': 'S'
                        }
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
                print("Table created successfully.")
            except self.db_manager.dynamodb.meta.client.exceptions.ResourceInUseException:
                print("Table already exists.")

    def save_card_info(self, user_id, card_info):
        return self.db_manager.save_card_info(user_id, card_info)

    def get_card_info(self, name):
        if self.db_manager.db_mode == 'postgres':
            conn = self.db_manager.get_postgres_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM payment_cards WHERE name = %s', (name,))
            result = cursor.fetchone()
            cursor.close()
            return result
        elif self.db_manager.db_mode == 'dynamodb':
            table = self.db_manager.dynamodb.Table('payment_cards')
            response = table.get_item(Key={'name': name})
            return response.get('Item')

    def process_payment(self, amount):
        # This is a placeholder for actual payment processing logic
        # In a real application, you would integrate with a payment gateway here
        print(f"Processing payment of ${amount}")
        return True  # Always return True for this example
