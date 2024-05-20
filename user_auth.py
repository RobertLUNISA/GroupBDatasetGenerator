import boto3
import logging
import streamlit as st

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load AWS Cognito configuration from Streamlit secrets
COGNITO_USER_POOL_ID = st.secrets["cognito"]["COGNITO_USER_POOL_ID"]
COGNITO_APP_CLIENT_ID = st.secrets["cognito"]["COGNITO_APP_CLIENT_ID"]
COGNITO_USER_POOL_IDENTITY_POOL_ID = st.secrets["cognito"]["COGNITO_USER_POOL_IDENTITY_POOL_ID"]
COGNITO_IDENTITY_POOL_ID = st.secrets["cognito"]["COGNITO_IDENTITY_POOL_ID"]
AWS_DEFAULT_REGION = st.secrets["aws"]["AWS_DEFAULT_REGION"]
AWS_ACCESS_KEY_ID = st.secrets["aws"]["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"]

# Initialize Cognito and Identity clients
cognito_client = boto3.client('cognito-idp', 
                              region_name=AWS_DEFAULT_REGION,
                              aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
identity_client = boto3.client('cognito-identity', 
                               region_name=AWS_DEFAULT_REGION,
                               aws_access_key_id=AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

# Function to sign up a new user
def signup_user(email, password):
    try:
        response = cognito_client.sign_up(
            ClientId=COGNITO_APP_CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email}
            ]
        )
        logging.info(f"Sign up response: {response}")

        # Confirm the user sign up
        response_admin_confirm = cognito_client.admin_confirm_sign_up(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=email
        )
        logging.info(f"User {email} confirmed successfully: {response_admin_confirm}")
        return response
    except cognito_client.exceptions.UsernameExistsException:
        logging.error("User already exists")
        return None
    except cognito_client.exceptions.InvalidParameterException as e:
        logging.error(f"Invalid parameters provided: {e}")
        return None
    except cognito_client.exceptions.CodeMismatchException as e:
        logging.error(f"Invalid confirmation code provided: {e}")
        return None
    except cognito_client.exceptions.NotAuthorizedException as e:
        logging.error(f"Not authorized to confirm user: {e}")
        return None
    except cognito_client.exceptions.UserNotFoundException as e:
        logging.error(f"User not found: {e}")
        return None
    except Exception as e:
        logging.error(f"Error signing up: {e}")
        return None

# Function to authenticate a user and get tokens
def authenticate_user(email, password):
    try:
        logging.info(f"Attempting to authenticate user: {email}")
        response = cognito_client.initiate_auth(
            ClientId=COGNITO_APP_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )
        logging.info(f"Authentication response: {response}")
        return response
    except cognito_client.exceptions.NotAuthorizedException:
        logging.error("The username or password is incorrect")
        return None
    except cognito_client.exceptions.UserNotConfirmedException:
        logging.error("User is not confirmed")
        return None
    except Exception as e:
        logging.error(f"Error authenticating: {e}")
        return None

# Function to get temporary credentials using an ID token
def get_temp_credentials(id_token):
    try:
        logging.info("Getting temporary credentials")
        identity_id_response = identity_client.get_id(
            IdentityPoolId=COGNITO_IDENTITY_POOL_ID,
            Logins={
                f'cognito-idp.{AWS_DEFAULT_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}': id_token
            }
        )
        identity_id = identity_id_response['IdentityId']
        logging.info(f"Identity ID response: {identity_id_response}")

        credentials_response = identity_client.get_credentials_for_identity(
            IdentityId=identity_id,
            Logins={
                f'cognito-idp.{AWS_DEFAULT_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}': id_token
            }
        )
        logging.info(f"Credentials response: {credentials_response}")
        return credentials_response['Credentials']
    except Exception as e:
        logging.error(f"Error getting temporary credentials: {e}")
        return None
