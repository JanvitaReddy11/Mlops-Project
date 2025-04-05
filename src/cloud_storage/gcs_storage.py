from google.cloud import storage
from google.cloud.exceptions import NotFound
from src.configuration.gcp_connection import GCSClient
import os
from io import StringIO
from typing import Union, List
import sys
import logging
import pickle
import pandas as pd
from pandas import DataFrame

class GoogleStorage:
    """
    A class for interacting with Google Cloud Storage, providing methods for file management,
    data uploads, and data retrieval in GCS buckets.
    """
    
    def __init__(self):
        """
        Initializes the GCSClient instance with GCS client and resource
        """
        gcs_client = GCSClient()
        self.storage_client = gcs_client.gcs_storage
        self.gcs_client = gcs_client.gcs_client

    def get_storage(self, storage_name: str):
        """
        Retrieves the GCS bucket object based on the provided bucket name.

        Args:
            storage_name (str): The name of the GCS bucket.

        Returns:
            Bucket: GCS bucket object.
        """
        try:
            bucket = self.storage_client.get_bucket(storage_name)
            return bucket
        except NotFound as e:
            raise Exception(f"Bucket {storage_name} not found") from e
        except Exception as e:
            raise Exception(f"Error retrieving bucket: {e}") from e
    
    def gcs_key_path_available(self, bucket_name: str, gcs_key: str) -> bool:
        """
        Checks if a specified GCS key path (file path) is available in the specified bucket.

        Args:
            bucket_name (str): Name of the GCS bucket.
            gcs_key (str): Key path of the file to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        try:
            bucket = self.get_storage(bucket_name)
            blob = bucket.blob(gcs_key)
            return blob.exists()
        except Exception as e:
            raise Exception(f"Error checking GCS key path: {e}") from e

    def read_object(self, object_name: str, decode: bool = True, make_readable: bool = False) -> Union[StringIO, str]:
        """
        Reads the specified GCS object with optional decoding and formatting.

        Args:
            object_name (str): The GCS object name.
            decode (bool): Whether to decode the object content as a string.
            make_readable (bool): Whether to convert content to StringIO for DataFrame usage.

        Returns:
            Union[StringIO, str]: The content of the object, as a StringIO or decoded string.
        """
        try:
            bucket = self.get_storage(object_name.split('/')[0])
            blob = bucket.blob('/'.join(object_name.split('/')[1:]))
            content = blob.download_as_text() if decode else blob.download_as_bytes()
            return StringIO(content) if make_readable else content
        except Exception as e:
            raise Exception(f"Error reading object from GCS: {e}") from e
    
    def get_file_object(self, filename: str, bucket_name: str) -> Union[List[object], object]:
        """
        Retrieves the file object(s) from the specified bucket based on the filename.

        Args:
            filename (str): The name of the file to retrieve.
            bucket_name (str): The name of the GCS bucket.

        Returns:
            Union[List[object], object]: The GCS file object or list of file objects.
        """
        try:
            bucket = self.get_storage(bucket_name)
            blobs = bucket.list_blobs(prefix=filename)
            blob_list = list(blobs)
            return blob_list[0] if len(blob_list) == 1 else blob_list
        except Exception as e:
            raise Exception(f"Error retrieving file object from GCS: {e}") from e

    def load_model(self, model_name: str, bucket_name: str, model_dir: str = None) -> object:
        """
        Loads a serialized model from the specified GCS bucket.

        Args:
            model_name (str): Name of the model file in the bucket.
            bucket_name (str): Name of the GCS bucket.
            model_dir (str): Directory path within the bucket.

        Returns:
            object: The deserialized model object.
        """
        try:
            model_file = f"{model_dir}/{model_name}" if model_dir else model_name
            bucket = self.get_storage(bucket_name)
            blob = bucket.blob(model_file)
            
            if not blob.exists():
                raise Exception(f"Model file {model_file} does not exist in bucket {bucket_name}")
                
            model_bytes = blob.download_as_bytes()
            model = pickle.loads(model_bytes)
            return model
        except Exception as e:
            raise Exception(f"Error loading model from GCS: {e}") from e
    
    def create_folder(self, folder_name: str, bucket_name: str) -> None:
        """
        Creates a folder in the specified GCS bucket.

        Args:
            folder_name (str): Name of the folder to create.
            bucket_name (str): Name of the GCS bucket.
        """
        try:
            bucket = self.get_storage(bucket_name)
            folder_blob = bucket.blob(folder_name + "/")
            if not folder_blob.exists():
                folder_blob.upload_from_string('')
        except Exception as e:
            raise Exception(f"Error creating folder in GCS: {e}") from e

    def upload_file(self, from_filename: str, to_filename: str, bucket_name: str, remove: bool = True):
        """
        Uploads a local file to the specified GCS bucket with an optional file deletion.

        Args:
            from_filename (str): Path of the local file.
            to_filename (str): Target file path in the bucket.
            bucket_name (str): Name of the GCS bucket.
            remove (bool): If True, deletes the local file after upload.
        """
        try:
            bucket = self.get_storage(bucket_name)
            blob = bucket.blob(to_filename)
            blob.upload_from_filename(from_filename)
            
            # Delete the local file if remove is True
            if remove and os.path.exists(from_filename):
                os.remove(from_filename)
        except Exception as e:
            raise Exception(f"Error uploading file to GCS: {e}") from e

    def upload_df_as_csv(self, data_frame: DataFrame, local_filename: str, bucket_filename: str, bucket_name: str) -> None:
        """
        Uploads a DataFrame as a CSV file to the specified GCS bucket.

        Args:
            data_frame (DataFrame): DataFrame to be uploaded.
            local_filename (str): Temporary local filename for the DataFrame.
            bucket_filename (str): Target filename in the bucket.
            bucket_name (str): Name of the GCS bucket.
        """
        try:
            # Save DataFrame to CSV locally and then upload it
            data_frame.to_csv(local_filename, index=None, header=True)
            self.upload_file(local_filename, bucket_filename, bucket_name)
        except Exception as e:
            raise Exception(f"Error uploading DataFrame to GCS: {e}") from e
    
    def get_df_from_object(self, bucket_name: str, object_path: str) -> DataFrame:
        """
        Converts a GCS object to a DataFrame.

        Args:
            bucket_name (str): The name of the GCS bucket.
            object_path (str): The path to the object in the bucket.

        Returns:
            DataFrame: DataFrame created from the object content.
        """
        try:
            bucket = self.get_storage(bucket_name)
            blob = bucket.blob(object_path)
            
            if not blob.exists():
                raise Exception(f"Object {object_path} does not exist in bucket {bucket_name}")
                
            content = blob.download_as_text()
            df = pd.read_csv(StringIO(content), na_values="na")
            return df
        except Exception as e:
            raise Exception(f"Error converting GCS object to DataFrame: {e}") from e

    def read_csv(self, filename: str, bucket_name: str) -> DataFrame:
        """
        Reads a CSV file from the specified GCS bucket and converts it to a DataFrame.

        Args:
            filename (str): The name of the file in the bucket.
            bucket_name (str): The name of the GCS bucket.

        Returns:
            DataFrame: DataFrame created from the CSV file.
        """
        try:
            return self.get_df_from_object(bucket_name, filename)
        except Exception as e:
            raise Exception(f"Error reading CSV from GCS: {e}") from e
            
    def download_file(self, bucket_name: str, source_blob_name: str, destination_file_name: str) -> None:
        """
        Downloads a file from the specified GCS bucket to the local filesystem.
        
        Args:
            bucket_name (str): The name of the GCS bucket.
            source_blob_name (str): The path to the file in the bucket.
            destination_file_name (str): The local file path where the file will be saved.
        """
        try:
            bucket = self.get_storage(bucket_name)
            blob = bucket.blob(source_blob_name)
            
            if not blob.exists():
                raise Exception(f"File {source_blob_name} does not exist in bucket {bucket_name}")
                
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)
            
            # Download the file
            blob.download_to_filename(destination_file_name)
            logging.info(f"Downloaded {source_blob_name} to {destination_file_name}")
        except Exception as e:
            raise Exception(f"Error downloading file from GCS: {e}") from e
            
    def list_files(self, bucket_name: str, prefix: str = None) -> List[str]:
        """
        Lists all files in a bucket with an optional prefix filter.
        
        Args:
            bucket_name (str): The name of the GCS bucket.
            prefix (str): Optional prefix to filter results.
            
        Returns:
            List[str]: List of file names in the bucket.
        """
        try:
            bucket = self.get_storage(bucket_name)
            blobs = bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            raise Exception(f"Error listing files in GCS bucket: {e}") from e
            
    def delete_file(self, bucket_name: str, file_path: str) -> None:
        """
        Deletes a file from the specified GCS bucket.
        
        Args:
            bucket_name (str): The name of the GCS bucket.
            file_path (str): The path to the file in the bucket.
        """
        try:
            bucket = self.get_storage(bucket_name)
            blob = bucket.blob(file_path)
            
            if not blob.exists():
                logging.warning(f"File {file_path} does not exist in bucket {bucket_name}")
                return
                
            blob.delete()
            logging.info(f"Deleted file {file_path} from bucket {bucket_name}")
        except Exception as e:
            raise Exception(f"Error deleting file from GCS: {e}") from e