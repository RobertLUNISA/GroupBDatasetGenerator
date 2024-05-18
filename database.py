import boto3
from io import StringIO
import os
from dotenv import load_dotenv
from user_auth import get_temp_credentials

# Load environment variables
load_dotenv()

# Function to upload a DataFrame to S3 as a CSV file
def upload_csv_to_s3(df, bucket_name, folder_route, file_path, is_synthetic=False, id_token=None):
    """Upload a DataFrame to S3 as a CSV file, supporting different folders for synthetic and existing datasets."""
    if is_synthetic and id_token:
        # Get temporary credentials if the dataset is synthetic
        credentials = get_temp_credentials(id_token)
        if not credentials:
            print("Failed to get temporary credentials.")
            return None

        # Initialize S3 client with temporary credentials
        s3 = boto3.client(
            's3',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretKey'],
            aws_session_token=credentials['SessionToken'],
            region_name=os.getenv('AWS_DEFAULT_REGION')
        )
    else:
        # Initialize S3 client with static credentials from environment variables
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION')
        )

    # Convert DataFrame to CSV and prepare for upload
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    csv_filename = os.path.basename(file_path)
    
    if is_synthetic:
        folder_route = "synthetic/"
    full_s3_path = f"{folder_route}{csv_filename}"
    
    try:
        # Upload the CSV file to S3
        s3.put_object(Bucket=bucket_name, Key=full_s3_path, Body=csv_buffer.getvalue())
        print("File uploaded successfully to S3.")
        return full_s3_path
    except Exception as e:
        print(f"Failed to upload file: {e}")
        return None

# Function to check if a dataset already exists in S3
def check_dataset_exists(bucket_name, folder_route, file_path):
    s3 = boto3.client('s3')
    csv_filename = os.path.basename(file_path)
    full_s3_path = f"{folder_route}{csv_filename}"
    try:
        # Check if the object exists in S3
        s3.head_object(Bucket=bucket_name, Key=full_s3_path)
        return True  # Object exists
    except s3.exceptions.ClientError:
        return False  # Object does not exist
