import os
import sys
from pandas import DataFrame
from sklearn.model_selection import train_test_split
from src.entity.config_entity import DataIngestionConfig
from src.entity.artifact_entity import DataIngestionArtifact
from src.exception import MyException
from src.logger import logging
from src.data_access.proj1_data import ProjData


class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig = DataIngestionConfig()):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise MyException(e, sys)

    def export_data_into_feature_store(self) -> DataFrame:
        try:
            logging.info('Collecting data from MongoDB')
            my_data = ProjData()
            dataframe = my_data.export_collection_as_dataframe(collection_name='Mlops-Proj', database_name='Project')
            logging.info(f"Dataframe shape: {dataframe.shape}")
            
            feature_store_file_path = self.data_ingestion_config.featutre_store_file_path
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            
            logging.info(f'Saving data in feature store at {feature_store_file_path}')
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            logging.info('Data saved successfully.')
            return dataframe
        except Exception as e:
            raise MyException(e, sys)

    def split_data_as_train_test(self, dataframe: DataFrame) -> None:
        try:
    
            test_size = self.data_ingestion_config.train_test_split_ratio if hasattr(self.data_ingestion_config, 'train_test_split_ratio') else 0.1
            train_set, test_set = train_test_split(dataframe, test_size=test_size)
            logging.info('Performed train-test split.')
        
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)
        
            logging.info(f"Exporting train and test datasets...")
            train_set.to_csv(self.data_ingestion_config.training_file_path, index=False, header=True)
            test_set.to_csv(self.data_ingestion_config.testing_file_path, index=False, header=True)

            logging.info(f"Exported train and test datasets to {self.data_ingestion_config.training_file_path} and {self.data_ingestion_config.testing_file_path}.")
        except Exception as e:
            raise MyException(e, sys)

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        try:
            dataframe = self.export_data_into_feature_store()
            logging.info('Data successfully retrieved from MongoDB.')
            self.split_data_as_train_test(dataframe)

            data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )
            return data_ingestion_artifact
        except Exception as e:
            raise MyException(e, sys) from e
