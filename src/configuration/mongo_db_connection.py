import os
import sys
import pymongo
import certifi

from src.exception import MyException
from src.logger import logging
from src.constants import DATABASE_NAME

from pymongo import MongoClient


# Load the certificate authority file to avoid timeout errors when connecting to MongoDB
ca = certifi.where()
#from dotenv import load_dotenv
#load_dotenv()

class MongoDBClient:


    client = None  # Shared MongoClient instance across all MongoDBClient instances

    def __init__(self, database_name: str = DATABASE_NAME) -> None:
   
        try:
            #if MongoDBClient.client is None:
            mongo_db_url = "mongodb+srv://Janvita_Reddy:Mongodb1@cluster0.xoup3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
            print(mongo_db_url)

            MongoDBClient.client = MongoClient(mongo_db_url, tlsCAFile=ca)
                
            # Use the shared MongoClient for this instance
            self.client = MongoDBClient.client
            self.database = self.client[database_name]  # Connect to the specified database
            self.database_name = database_name
            logging.info("MongoDB connection successful.")
            
        except Exception as e:
            # Raise a custom exception with traceback details if connection fails
            raise MyException(e, sys)