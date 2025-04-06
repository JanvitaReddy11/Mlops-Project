from google.cloud import storage
import os
from src.constants import  REGION_NAME
from dotenv import load_dotenv


class GCSClient:
    gcs_client = None
    gcs_storage = None

    def __init__(self, region_name=REGION_NAME):
        if GCSClient.gcs_storage is None or GCSClient.gcs_client is None:
            #load_dotenv(dotenv_path="C:/Users/reddy/Downloads/Mlops-Project/.env")
            #credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            
            #if credentials_path is None:
                #raise Exception("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
                
            #GCSClient.gcs_storage = storage.Client.from_service_account_json(credentials_path)
            GCSClient.gcs_storage = storage.Client() 
            GCSClient.gcs_client = GCSClient.gcs_storage
        
        self.gcs_storage = GCSClient.gcs_storage
        self.gcs_client = GCSClient.gcs_client