# Import necessary modules
import numpy as np
import pandas as pd
from datetime import datetime
from database import upload_csv_to_s3
import validator
import streamlit as st

# Function to generate a linear regression dataset
def linear_regression_dataset(column_counts=9, row_counts=1000):
    features = []

    for i in range(column_counts - 1):
        if i < 3:
            if i == 0:
                features.append(np.random.normal(20, 5, row_counts))
            elif i == 1:
                features.append(np.random.normal(50, 10, row_counts))
            else:
                features.append(np.random.uniform(0, 1, row_counts))
        else:
            features.append(np.random.normal(0, 0.1, row_counts))

    y = 2 * features[0] + 0.5 * features[1] + 10 * features[2] + np.random.normal(0, 2, row_counts)
    column_names = [f'Feature_{i+1}' for i in range(column_counts - 1)] + ['Target']
    X = pd.DataFrame(np.column_stack(features + [y]), columns=column_names)

    return X

# Function to generate a random forest dataset
def random_forest_dataset(column_counts=9, row_counts=1000):
    features = []

    for i in range(column_counts - 1):
        if i == 0:
            features.append(np.random.normal(0, 1, row_counts))
        elif i == 1:
            features.append(np.random.normal(5, 2, row_counts))
        elif i == 2:
            features.append(np.random.randint(0, 3, row_counts))
        elif i == 3:
            features.append(features[0] * features[1])
        elif i == 4:
            features.append(np.random.choice([0, 1], size=row_counts, p=[0.7, 0.3]))
        else:
            features.append(np.random.normal(0, 1, row_counts))

    y = (features[0]**2 + np.sin(features[1]) + features[2] > np.median(features[0]**2 + np.sin(features[1]) + features[2])).astype(int)
    feature_names = [f'Feature_{i+1}' for i in range(column_counts - 1)]
    X = pd.DataFrame(np.column_stack(features), columns=feature_names)
    X['Target'] = y

    return X

# Function to generate a k-nearest-neighbors dataset
def knn_dataset(column_counts=9, row_counts=1000):
    features = []

    for i in range(column_counts - 1):
        if i == 0:
            features.append(np.random.normal(0, 1, row_counts))
        elif i == 1:
            features.append(np.sin(features[0]) + np.random.normal(0, 0.1, row_counts))
        elif i == 2:
            features.append(features[0]**2 + np.random.normal(0, 1, row_counts))
        elif i == 3:
            features.append(np.random.choice([0, 1, 2], size=row_counts))
        else:
            features.append(np.random.normal(0, 1, row_counts))

    y = (2*features[0] - features[1] + features[2] + 5*np.where(features[3] == 2, 1, 0) > 1).astype(int)
    column_names = [f'Feature_{i+1}' for i in range(column_counts - 1)]
    X = pd.DataFrame(np.column_stack(features), columns=column_names)
    X['Target'] = y

    return X

# Function to generate a dataset based on the specified algorithm
def dataset_generator(algorithm, size, features):
    row_counts = 499 if size == "less than 500" else 501
    column_counts = 9 if features == 'less than 10' else 10

    if algorithm == 'Linear Regression':
        return linear_regression_dataset(column_counts=column_counts, row_counts=row_counts)
    elif algorithm == 'Random Forest':
        return random_forest_dataset(column_counts=column_counts, row_counts=row_counts)
    elif algorithm == 'k-nearest-neighbors':
        return knn_dataset(column_counts=column_counts, row_counts=row_counts)
    else:
        raise ValueError(f"Unsupported algorithm specified: {algorithm}")

# Main function to generate and validate a synthetic dataset
def main(algorithm, size, features, id_token):
    print("Validating the Synthetic Dataset")
    while True:
        data = dataset_generator(algorithm, size, features)
        path = f"Synthetic_Dataset_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        target_variable = 'Target'
        algorithm_index = data.columns.get_loc(target_variable)
        clean_df, valid = validator.validator(data, algorithm_index, target_variable)
        if valid:
            object_key = upload_csv_to_s3(clean_df, st.secrets["aws"]["AWS_S3_BUCKET"], "", path, is_synthetic=True, id_token=id_token)
            if object_key:
                print(f"*** Dataset uploaded successfully. ***")
                return object_key
            else:
                print("*** Generating New Synthetic Dataset ***")
        else:
            print("*** Dataset validation failed ***")

