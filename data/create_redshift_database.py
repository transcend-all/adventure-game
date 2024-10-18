import boto3
import json
import time
from botocore.exceptions import ClientError

# Configuration - replace these with your actual configurations
REGION = 'us-west-1'  
WORKGROUP = 'adventure-game'  
SECRET_ARN = "arn:aws:secretsmanager:us-west-1:783764591058:secret:redshift/serverless/evansecrety-WilCQY"
INITIAL_DATABASE = 'dev'
NEW_DATABASE_NAME = 'adventure-game-db'  

# Initialize the Redshift Data API client
redshift_data_client = boto3.client('redshift-data', region_name=REGION)

def get_secret(secret_name, region_name):
    """
    Fetch the secret from AWS Secrets Manager.
    """
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
    
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)  # Return the secret as a dictionary
    except ClientError as e:
        print(f"Failed to retrieve secret: {e}")
        raise e

def validate_credentials(secret_arn, workgroup_name, database):
    """
    Try a simple SQL query to validate the credentials.
    """
    sql = "SELECT 1;"  # Simple query to test credentials
    try:
        response = redshift_data_client.execute_statement(
            Database=database,
            SecretArn=secret_arn,
            Sql=sql,
            WorkgroupName=workgroup_name
        )
        statement_id = response['Id']
        print(f"Validation query executed with ID: {statement_id}")
        return True  # Credentials are valid if no exception is raised
    except ClientError as e:
        print(f"Credential validation failed: {e}")
        return False  # Return False if validation fails

def execute_sql_statement(sql, secret_arn, workgroup_name, database):
    """
    Executes a SQL statement using the Redshift Data API.
    """
    try:
        response = redshift_data_client.execute_statement(
            Database=database,
            SecretArn=secret_arn,
            Sql=sql,
            WorkgroupName=workgroup_name
        )
        statement_id = response['Id']
        print(f"Executed statement with ID: {statement_id}")
        return statement_id
    except ClientError as e:
        print(f"Error executing statement: {e}")
        raise e

def check_statement_status(statement_id):
    """
    Polls the status of the executed statement until completion.
    """
    while True:
        try:
            response = redshift_data_client.describe_statement(Id=statement_id)
            status = response['Status']
            print(f"Statement Status: {status}")
            if status in ['FINISHED', 'FAILED', 'ABORTED']:
                if status == 'FINISHED':
                    print("Statement executed successfully.")
                else:
                    print(f"Statement failed with status: {status}")
                    print(f"Error: {response.get('Error')}")
                break
            time.sleep(2)  # Wait for 2 seconds before polling again
        except ClientError as e:
            print(f"Error checking statement status: {e}")
            raise e

def create_database(secret_arn, workgroup_name, database_name):
    """
    Creates a new database in Redshift Serverless.
    """
    sql = f"CREATE DATABASE \"{database_name}\";"
    print(f"Executing SQL: {sql}")
    statement_id = execute_sql_statement(sql, secret_arn, workgroup_name, INITIAL_DATABASE)
    check_statement_status(statement_id)

def main():
    secret_name = "redshift/serverless/evansecrety"
    region_name = REGION
    
    try:
        # Step 1: Get the secret
        secret = get_secret(secret_name, region_name)
        print("Secret retrieved successfully.")
        
        # Step 2: Validate the credentials
        if validate_credentials(SECRET_ARN, WORKGROUP, INITIAL_DATABASE):
            print("Credentials validated successfully, proceeding with database creation...")
            
            # Step 3: Proceed to create the database
            create_database(SECRET_ARN, WORKGROUP, NEW_DATABASE_NAME)
        else:
            print("Invalid credentials. Aborting database creation.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
