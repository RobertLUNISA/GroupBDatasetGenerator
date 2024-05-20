import re
import boto3
from boto3.dynamodb.conditions import Attr
import pandas as pd
import numpy as np
from botocore.exceptions import NoCredentialsError, ClientError
import streamlit as st
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Setup AWS clients using Streamlit secrets
s3_client = boto3.client(
    's3',
    aws_access_key_id=st.secrets["aws"]["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"],
    region_name=st.secrets["aws"]["AWS_DEFAULT_REGION"]
)
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=st.secrets["aws"]["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"],
    region_name=st.secrets["aws"]["AWS_DEFAULT_REGION"]
)
AWS_S3_BUCKET = st.secrets["aws"]["AWS_S3_BUCKET"]

# Function to generate a presigned URL for S3 objects
def generate_presigned_url(bucket_name, object_key, expiration=3600):
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name, 'Key': object_key},
                                                    ExpiresIn=expiration)
        logging.info(f"Generated presigned URL: {response}")
        return response
    except ClientError as e:
        logging.error(f"Error generating presigned URL: {e}")
        return None

# Function to introduce noise/errors into a dataset
def make_dataset_unclean(dataframe, error_rate=0.05):
    n_changes = int(np.ceil(error_rate * dataframe.size))

    for _ in range(n_changes):
        row_idx = np.random.randint(0, dataframe.shape[0])
        col_idx = np.random.randint(0, dataframe.shape[1])

        if np.random.rand() > 0.5:
            dataframe.iat[row_idx, col_idx] = np.nan
        else:
            col = dataframe.iloc[:, col_idx]
            dataframe.iat[row_idx, col_idx] = np.random.choice(col.dropna().values) if col.dropna().values.size > 0 else np.nan

    return dataframe

# Function to fetch dataset metadata from DynamoDB
def fetch_dataset_metadata(input_algorithm, features, instances, topic, cleanliness):
    table = dynamodb.Table('DatasetMetadata')

    input_algorithm = input_algorithm.replace(' ', '-').lower()
    topic = topic.capitalize()

    logging.info(f"Inputs - Algorithm: {input_algorithm}, Features: {features}, Instances: {instances}, Topic: {topic}, Cleanliness: {cleanliness}")

    filter_expression = Attr('Machine Learning Task').eq(input_algorithm)

    if features == 'less than 10':
        filter_expression &= Attr('Number of Features').lt(10)
    elif features == '10 or more':
        filter_expression &= Attr('Number of Features').gte(10)
        
    if instances == 'less than 500':
        filter_expression &= Attr('Number of Instances').lt(500)
    elif instances == '500 or more':
        filter_expression &= Attr('Number of Instances').gte(500)
    
    filter_expression &= Attr('Topic').eq(topic)
    
    logging.info(f"Combined Filter Expression: {filter_expression}")

    try:
        response = table.scan(
            FilterExpression=filter_expression
        )
        logging.info(f"Combined Filter Response: {response}")
        return response['Items'] if 'Items' in response else []
    except Exception as e:
        logging.error(f"Error fetching data from DynamoDB: {e}")
        return []

# Function to validate password requirements
def password_requirements(password):
    if (len(password) < 8 or
        not re.search(r"\d", password) or
        not re.search(r"[A-Z]", password) or
        not re.search(r"[a-z]", password) or
        not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)):
        return False
    return True
