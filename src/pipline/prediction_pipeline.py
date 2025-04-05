import sys
from src.entity.config_entity import DiabetesPredictorConfig
from src.entity.gcs_estimator import Proj1Estimator
from src.exception import MyException
from src.logger import logging
from pandas import DataFrame

class DiabetesData:
    def __init__(self,
                 Pregnancies: int,
                 Glucose: float,
                 BloodPressure: float,
                 SkinThickness: float,
                 Insulin: float,
                 BMI: float,
                 DiabetesPedigreeFunction: float,
                 Age: int,
                 ):
        """
        DiabetesData constructor to initialize all fields for prediction
        """
        try:
            self.Pregnancies = Pregnancies
            self.Glucose = Glucose
            self.BloodPressure = BloodPressure
            self.SkinThickness = SkinThickness
            self.Insulin = Insulin
            self.BMI = BMI
            self.DiabetesPedigreeFunction = DiabetesPedigreeFunction
            self.Age = Age
           

        except Exception as e:
            raise MyException(e, sys) from e

    def get_diabetes_input_dataframe(self) -> DataFrame:
        """
        Returns the input as a pandas DataFrame
        """
        try:
            diabetes_input_dict = self.get_diabetes_data_as_dict()
            return DataFrame(diabetes_input_dict)
        except Exception as e:
            raise MyException(e, sys) from e

    def get_diabetes_data_as_dict(self) -> dict:
        """
        Returns the input as a dictionary
        """
        logging.info("Creating diabetes data dictionary from class attributes")

        try:
            input_data = {
                "Pregnancies": [self.Pregnancies],
                "Glucose": [self.Glucose],
                "BloodPressure": [self.BloodPressure],
                "SkinThickness": [self.SkinThickness],
                "Insulin": [self.Insulin],
                "BMI": [self.BMI],
                "DiabetesPedigreeFunction": [self.DiabetesPedigreeFunction],
                "Age": [self.Age],
               
            }

            logging.info("Created diabetes data dict successfully")
            return input_data
        except Exception as e:
            raise MyException(e, sys) from e


class DiabetesClassifier:
    def __init__(self, prediction_pipeline_config: DiabetesPredictorConfig = DiabetesPredictorConfig()) -> None:
        """
        Loads prediction configuration
        """
        try:
            self.prediction_pipeline_config = prediction_pipeline_config
        except Exception as e:
            raise MyException(e, sys)

    def predict(self, dataframe: DataFrame) -> str:
        """
        Predicts the diabetes outcome using trained model
        """
        try:
            logging.info("Initiating diabetes prediction")
            model = Proj1Estimator(
                storage_name=self.prediction_pipeline_config.storage_name,
                model_path=self.prediction_pipeline_config.model_file_path,
            )

            result = model.predict(dataframe)
            return result

        except Exception as e:
            raise MyException(e, sys)
