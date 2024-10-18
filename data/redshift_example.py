import boto3
import pandas as pd
import uuid
import time
import os
from botocore.exceptions import ClientError

# Configuration - replace these with your actual configurations
S3_BUCKET = 'adventure-game-data'
REDHSIFT_NAMESPACE = 'adventure-game'
REDHSIFT_WORKGROUP = 'adventure-game'
DATABASE_NAME = 'your-database-name'
DATABASE_USER = 'your-database-user'
REGION = 'us-west-1'  # Replace with your AWS region

def upload_csv_to_s3(file_path, bucket, s3_key):
    """
    Uploads a file to S3.
    """
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_path, bucket, s3_key)
        print(f"Uploaded {file_path} to s3://{bucket}/{s3_key}")
    except ClientError as e:
        print(f"Failed to upload {file_path} to S3: {e}")
        raise e

def execute_copy_command(s3_path, table_name, iam_role_arn):
    """
    Executes the Redshift COPY command to load data from S3.
    """
    redshift_data_client = boto3.client('redshift-data', region_name=REGION)
    
    copy_command = f"""
        COPY {table_name}
        FROM '{s3_path}'
        IAM_ROLE '{iam_role_arn}'
        CSV
        IGNOREHEADER 1
        TIMEFORMAT 'epochsecs'
        REGION '{REGION}';
    """
    
    try:
        response = redshift_data_client.execute_statement(
            ClusterIdentifier=None,  # Not needed for Serverless
            Database=DATABASE_NAME,
            DbUser=DATABASE_USER,
            Sql=copy_command,
            StatementName=f"copy_{table_name}_{uuid.uuid4()}",
            WithEvent=True,
            Namespace=REDHSIFT_NAMESPACE,
            WorkgroupName=REDHSIFT_WORKGROUP
        )
        statement_id = response['Id']
        print(f"Executing COPY command with Statement ID: {statement_id}")
        return statement_id
    except ClientError as e:
        print(f"Failed to execute COPY command: {e}")
        raise e

def check_statement_completion(statement_id):
    """
    Polls the statement status until it's finished.
    """
    redshift_data_client = boto3.client('redshift-data', region_name=REGION)
    
    while True:
        response = redshift_data_client.describe_statement(Id=statement_id)
        status = response['Status']
        if status in ['FINISHED', 'FAILED', 'ABORTED']:
            print(f"Statement {statement_id} finished with status: {status}")
            if status == 'FAILED':
                print(f"Error: {response.get('Error')}")
            break
        print("Waiting for statement to complete...")
        time.sleep(2)

def load_csv_to_redshift(file_path, table_name, iam_role_arn):
    """
    Orchestrates the process of uploading CSV to S3 and loading it into Redshift.
    """
    # Generate a unique S3 key
    s3_key = f"uploads/{uuid.uuid4()}_{os.path.basename(file_path)}"
    upload_csv_to_s3(file_path, S3_BUCKET, s3_key)
    
    # Construct the S3 path
    s3_path = f"s3://{S3_BUCKET}/{s3_key}"
    
    # Execute the COPY command
    statement_id = execute_copy_command(s3_path, table_name, iam_role_arn)
    
    # Check the status of the COPY command
    check_statement_completion(statement_id)

if __name__ == "__main__":
    # Example usage
    csv_file_path = 'path_to_your_file.csv'  # Replace with your CSV file path
    target_table = 'your_target_table'       # Replace with your Redshift table name
    iam_role_arn = 'arn:aws:iam::123456789012:role/YourRedshiftRole'  # Replace with your IAM role ARN
    
    load_csv_to_redshift(csv_file_path, target_table, iam_role_arn)
