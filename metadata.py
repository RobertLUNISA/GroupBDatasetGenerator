import boto3
import streamlit as st
import os

# Function to extract and upload metadata to DynamoDB
def extract_and_upload_metadata(data, algorithm_name, bucket_name, file_path, object_key, target_variable):
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=st.secrets["aws"]["AWS_ACCESS_KEY_ID"],
                              aws_secret_access_key=st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"],
                              region_name=st.secrets["aws"]["AWS_DEFAULT_REGION"])

    try:
        table = dynamodb.Table('DatasetMetadata')
        dataset_name = input("What is the dataset name? ")
        topic = input("Enter the topic (1 for Health, 2 for Finance, 3 for Entertainment, 4 for Technology, 5 for Education): ")
        topics = {1: "Health", 2: "Finance", 3: "Entertainment", 4: "Technology", 5: "Education"}
        source_link = input("Enter the source link: ")
        size_in_kb = os.path.getsize(file_path) // 1024

        response = table.put_item(
            Item={
                'Dataset Name': dataset_name,
                'Machine Learning Task': algorithm_name,
                'Topic': topics[int(topic)],
                'Number of Instances': int(data.shape[0]),
                'Number of Features': int(data.shape[1]),
                'Size in KB': size_in_kb,
                'Source Link': source_link,
                'S3ObjectKey': object_key,
                'Target Variable': target_variable
            }
        )
        print("Metadata uploaded successfully to DynamoDB.")
    except Exception as e:
        print(f"Failed to upload metadata: {e}")
