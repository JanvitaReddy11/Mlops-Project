import json
import sys
import os

import pandas as pd
from pandas import DataFrame

from src.exception import MyException
from src.logger import logging
from src.utils.main_utils import read_yaml_file
from src.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from src.entity.config_entity import DataValidationConfig
from src.constants import SCHEMA_FILE_PATH

class DataValidation:

    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)
        except Exception as e:
            raise MyException(e, sys)

    def validate_num_columns(self, df: DataFrame) -> bool:
        try:
            status = len(df.columns) == len(self._schema_config['columns'])
            logging.info(f"Required columns present in dataset: {status}")
            return status
        except Exception as e:
            raise MyException(e, sys)

    def column_exist(self, df: DataFrame) -> bool:
        try:
            df_columns = df.columns
            miss_num_columns = []
            for col in self._schema_config['numerical_columns']:
                if col not in df_columns:
                    miss_num_columns.append(col)

            if miss_num_columns:
                logging.info(f"Numerical columns missing: {miss_num_columns}")
            return len(miss_num_columns) == 0
        except Exception as e:
            raise MyException(e, sys)

    @staticmethod
    def read_data(file_path) -> DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise MyException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            val_msg = ""
            logging.info('Initiated the validation pipeline')

            # Reading train and test data
            train_df = DataValidation.read_data(file_path=self.data_ingestion_artifact.trained_file_path)
            test_df = DataValidation.read_data(file_path=self.data_ingestion_artifact.test_file_path)

            # Validate number of columns
            status = self.validate_num_columns(train_df)
            if not status:
                val_msg += f"Columns are missing in train dataset and not equal to the expected\n"
            else:
                logging.info(f'All columns are present in train dataset')

            status = self.validate_num_columns(test_df)
            if not status:
                val_msg += f"Columns are missing in test dataset and not equal to the expected\n"
            else:
                logging.info(f'All columns are present in test dataset')

            # Validate numerical columns existence
            status = self.column_exist(train_df)
            if not status:
                val_msg += f"Numerical columns are missing in train dataset\n"
            else:
                logging.info(f'All numerical columns are present in train dataset')

            status = self.column_exist(test_df)
            if not status:
                val_msg += f"Numerical columns are missing in test dataset\n"
            else:
                logging.info(f'All numerical columns are present in test dataset')

            # Final validation status
            val_status = len(val_msg) == 0

            # Creating the data validation artifact and report
            data_validation_artifact = DataValidationArtifact(
                validation_status=val_status,
                message=val_msg,
                validation_report_file_path=self.data_validation_config.validation_report_file_path
            )

            # Report directory creation if not exists
            report_dir = os.path.dirname(self.data_validation_config.validation_report_file_path)
            os.makedirs(report_dir, exist_ok=True)

            validation_report = {
                "validation_status": val_status,
                "message": val_msg.strip()
            }

            # Writing the validation report to file
            with open(self.data_validation_config.validation_report_file_path, "w") as report_file:
                json.dump(validation_report, report_file, indent=4)

            logging.info('Data Validation artifact created')
            return data_validation_artifact

        except Exception as e:
            raise MyException(e, sys)
