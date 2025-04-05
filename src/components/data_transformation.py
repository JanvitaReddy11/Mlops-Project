from src.entity.config_entity import DataTransformationConfig
from src.entity.artifact_entity import DataTransformationArtifact, DataIngestionArtifact, DataValidationArtifact
from src.exception import MyException
from src.logger import logging
from src.utils.main_utils import save_object, save_numpy_array_data, read_yaml_file
from src.constants import TARGET_COLUMN, SCHEMA_FILE_PATH, CURRENT_YEAR
import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE
from sklearn import preprocessing
import sys

class DataTransformation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_transformation_config: DataTransformationConfig,
                 data_validation_artifact: DataValidationArtifact):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_transformation_config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact
            self._schema_config = read_yaml_file(file_path=SCHEMA_FILE_PATH)
        except Exception as e:
            raise MyException(e, sys)

    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise MyException(e, sys)

    def _data_imbalance(self, train_x, train_y):
        # Apply SMOTE (Synthetic Minority Over-sampling Technique) for handling class imbalance in training data
        smote = SMOTE(random_state=42)
        X_oversampled, y_oversampled = smote.fit_resample(train_x, train_y)
        return X_oversampled, y_oversampled

    def _standard_scaling(self, x):
        # Standardize the features (mean = 0, std = 1)
        pre_process = preprocessing.StandardScaler().fit(x) 
        x_transform = pre_process.transform(x)  
        return x_transform, pre_process  
    
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            logging.info("Data Transformation Started !!!")
            if not self.data_validation_artifact.validation_status:
                raise Exception(self.data_validation_artifact.message)
            train_df = self.read_data(file_path=self.data_ingestion_artifact.trained_file_path)
            test_df = self.read_data(file_path=self.data_ingestion_artifact.test_file_path)
            logging.info("Train-Test data loaded")
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_train_df = train_df[TARGET_COLUMN]
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            logging.info("Input and Target columns defined for both train and test data.")

            input_balance_train, target_balance_train = self._data_imbalance(input_feature_train_df, target_feature_train_df)
            logging.info("Applied SMOTE to handle data imbalance in the training dataset.")

            # Standardize the input features for both training and test data
            input_transform_train, pre_process = self._standard_scaling(input_balance_train)
            input_transform_test, _ = self._standard_scaling(input_feature_test_df)  

            # Prepare the final train and test arrays (features + target labels)
            train_arr = np.c_[input_transform_train, np.array(target_balance_train)]
            test_arr = np.c_[input_transform_test, np.array(target_feature_test_df)]
            logging.info("Feature-target concatenation done for both train and test data.")

            save_object(self.data_transformation_config.transformed_object_file_path, pre_process)

            # Save the transformed training and testing data
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)
            logging.info("Saving transformation object and transformed files.")
            logging.info("Data transformation completed successfully.")
            return DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )

        except Exception as e:
            raise MyException(e, sys) from e
