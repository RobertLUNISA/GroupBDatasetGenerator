import pandas as pd
import os
import validator
from database import upload_csv_to_s3, check_dataset_exists
from metadata import extract_and_upload_metadata


def main():
    print("Welcome to the Dataset Validator!")
    while True:
        path = input("Please enter the path to your dataset or type 'exit' to quit: ")
        if path.lower() == 'exit':
            break

        try:
            data = pd.read_csv(path)
        except Exception as e:
            print(f"An error occurred while loading the dataset: {e}")
            continue

        print("\n" + "*" * 20 + "\n")
        target_variable = validator.user_select_target(data)

        print("\n" + "*" * 20 + "\n")
        algorithm_index = validator.select_algorithm()
        algorithms = {1: "linear-regression", 2: "random-forest", 3: "k-nearest-neighbors"}
        algorithm_name = algorithms[algorithm_index]

        if not algorithm_name:
            print("Invalid algorithm selection.")
            return

        if not validator.validate_algorithm_suitability(data, target_variable, algorithm_name):
            return

        folder_route = algorithm_name + "/"

        # Check for duplicate datasets in S3
        if check_dataset_exists("capstonedatasets", folder_route, path):
            print("A dataset with this name already exists in the selected category. Please rename your dataset.")
            continue

        print("\n" + "*" * 20 + "\n")
        clean_df, valid = validator.validator(data, algorithm_index, target_variable)
        if valid:
            object_key = upload_csv_to_s3(clean_df, "capstonedatasets", folder_route, path)
            if object_key:
                print(f"*** Dataset uploaded successfully. ***")
                print("*** Extracting metadata and uploading to DynamoDB ***")
                extract_and_upload_metadata(clean_df, algorithm_name, "capstonedatasets", path, object_key, target_variable)
                break  # Exit the loop since validation passed and file is uploaded
            else:
                print("*** Failed to upload file to S3 ***")
        else:
            print("*** Dataset validation failed ***")

if __name__ == "__main__":
    main()

