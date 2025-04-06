import sys
import pandas as pd
import numpy as np
from typing import Optional

from src.configuration.mongo_db_connection import MongoDBClient
from src.constants import DATABASE_NAME
from src.exception import MyException
from pymongo import MongoClient
#from dotenv import load_dotenv
#load_dotenv()
import os


class ProjData:
    """
    A class to export MongoDB records as a pandas DataFrame.
    """

    def __init__(self) -> None:
        """
        Initializes the MongoDB client connection.
        """
        #try:
            #self.mongo_client = MongoDBClient()
        #except Exception as e:
            #raise MyException(e, sys)

    def export_collection_as_dataframe(self, collection_name: str, database_name: Optional[str] = None) -> pd.DataFrame:
     
        try:
            print("Fetching data from MongoDB")

            # Use the initialized `database` from `MongoDBClient`
            #database = self.mongo_client.client[database_name]
            #collection = database[collection_name]
            mongo_db_url = os.getenv('MONGO_URL_KEY') 
            client = MongoClient(mongo_db_url, serverSelectionTimeoutMS=5000)  # Set timeout for connection
            client.admin.command('ping')
            data_basename = "Project"
            collection_name =  "Mlops-Proj"
            db = client[data_basename]
            collection = db[collection_name]

            df = pd.DataFrame(list(collection.find()))
            print(f"Data fetched with len: {len(df)}")

            if "_id" in df.columns:  # Drop MongoDB's default ID column if present
                df = df.drop(columns=["_id"], axis=1)
            df.replace({"na": np.nan}, inplace=True)

            return df

        except Exception as e:
            raise MyException(e, sys)
