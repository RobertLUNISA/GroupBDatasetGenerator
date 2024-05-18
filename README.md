# DataGenerator
A web application that generates a customised dataset based on the user needs

<!-- **Introduction** -->

Welcome to Dataset Generator! Before you run the application, you need to set up a few things. This document will guide you through the process of configuring your environment with necessary credentials and settings.
Prerequisites

    Python 3.12 installed
    Git (for cloning the repository)

Steps to Set Up Your Environment
1. Clone the Repository

First, clone the repository to your local machine:
```bash
git clone https://github.com/cuahunt7/DatasetGenerator.git
cd DatasetGenerator
```

2. Set Up Your Credentials

Since sensitive data such as API keys and credentials should not be tracked by Git, you need to set up your `.env` file manually:

**Create Your .env File**

* Copy the Sample File: A sample environment file named `.env.sample` is provided in the repository. Start by copying this file and renaming it to `.env`:
    ```bash
    cp .env.sample .env
    ```

* Edit the .`env` File: Open the `.env` file in a text editor of your choice:
    ```bash
    nano .env
    ```

* Replace the placeholder values with your actual credentials.
    * For example:
        AWS_ACCESS_KEY_ID=your_aws_access_key_id_here
        AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
        AWS_DEFAULT_REGION=your_aws_region_here
* Save and close the file.

3. Install Dependencies

Install the required Python dependencies:
```bash
pip3 install -r requirements.txt
```

4. Run the Application

Now, you are ready to run the application:
```bash
python3 main.py
```


## 5. AWS Services Configuration

### AWS Cognito

AWS Cognito is used for user authentication and management in the DatasetGenerator application. Below are the steps to set up AWS Cognito:

#### 5.1. Create a User Pool

1. Sign in to the AWS Management Console and open the Amazon Cognito console at [https://console.aws.amazon.com/cognito/](https://console.aws.amazon.com/cognito/).
2. Choose **Manage User Pools** and then choose **Create a user pool**.
3. Configure Sign-in Options:
    - Under **How do you want your end users to sign in?**, choose **Email address** or **Phone number**.
4. Configure Security Settings:
    - Set a password policy that meets your requirements.
    - Enable Multi-Factor Authentication (MFA) if necessary.
5. Configure Sign-up Experience:
    - Enable self-registration.
    - Set required attributes (e.g., email).
6. Configure Message Delivery:
    - Set up an email provider to send messages (using Amazon SES or default Cognito email service).

#### 5.2. Create an App Client

1. In the **App clients** section of your user pool, choose **Add an app client**.
2. Enter a name for your app client.
3. Ensure the following authentication flow settings are enabled:
    - **USER_PASSWORD_AUTH**
    - **ALLOW_REFRESH_TOKEN_AUTH**
4. Choose **Create app client**.

#### 5.3. Retrieve User Pool and App Client IDs

1. Go to the **General settings** section of your user pool.
2. Copy the **Pool Id**.
3. Go to the **App clients** section and copy the **App client id**.

#### 5.4. Update the `.env` File

Add the following information to your `.env` file:
```plaintext
COGNITO_USER_POOL_ID=your_cognito_user_pool_id_here
COGNITO_APP_CLIENT_ID=your_cognito_app_client_id_here
COGNITO_IDENTITY_POOL_ID=your_cognito_identity_pool_id_here
```
### S3 Bucket Configuration

The application uses an S3 bucket for dataset storage.

#### 5.5. Create an S3 Bucket

1. Sign in to the AWS Management Console and open the Amazon S3 console at [https://console.aws.amazon.com/s3/](https://console.aws.amazon.com/s3/).
2. Choose **Create bucket**.
3. Enter a **Bucket name** and choose a **Region**.
4. Configure Options and Permissions as needed.
5. Choose **Create bucket**.

#### 5.6. Update the `.env` File

Add the S3 bucket name to your `.env` file:
```plaintext
AWS_S3_BUCKET=your_s3_bucket_name_here
```

### DynamoDB Configuration
DynamoDB is used to store metadata about the datasets.

5.7. Create a DynamoDB Table
1. Sign in to the AWS Management Console and open the Amazon DynamoDB console at https://console.aws.amazon.com/dynamodb/.
2. Choose Create table.
3. Enter a Table name (e.g., DatasetMetadata).
4. Define the Primary key:
- Partition key: DatasetName (String)
5. Configure Table Settings as needed and choose Create.
#### 5.8. Update the .env File
Add the DynamoDB table name to your .env file:

```plaintext
DYNAMODB_TABLE_NAME=dynamodb_table_name_here
```
