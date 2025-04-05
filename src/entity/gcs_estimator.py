from src.cloud_storage.gcs_storage import GoogleStorage
from src.exception import MyException
from src.entity.estimator import MyModel
import sys
from pandas import DataFrame


class Proj1Estimator:
    """
    This class is used to save and retrieve our model from GCS bucket and to do prediction
    """

    def __init__(self, storage_name, model_path):
        """
        :param storage_name: Name of your model bucket
        :param model_path: Location of your model in GCS
        """
        self.storage_name = storage_name  # Changed variable name for consistency
        self.gcs = GoogleStorage()
        self.model_path = model_path
        self.loaded_model: MyModel = None

    def is_model_present(self, model_path):
        try:
            return self.gcs.gcs_key_path_available(bucket_name=self.storage_name, gcs_key=model_path)
        except MyException as e:
            print(e)
            return False

    def load_model(self) -> MyModel:
        """
        Load the model from the model_path
        :return:
        """
        return self.gcs.load_model(self.model_path, bucket_name=self.storage_name)

    def save_model(self, from_file, remove: bool = False) -> None:
        """
        Save the model to the model_path
        :param from_file: Your local system model path
        :param remove: By default it is false that means you will have your model locally available in your system folder
        :return:
        """
        try:
            self.gcs.upload_file(from_file,
                                 to_filename=self.model_path,
                                 bucket_name=self.storage_name,
                                 remove=remove
                                 )
        except Exception as e:
            raise MyException(e, sys)

    def predict(self, dataframe: DataFrame):
        """
        :param dataframe:
        :return:
        """
        try:
            if self.loaded_model is None:
                self.loaded_model = self.load_model()
            return self.loaded_model.predict(dataframe=dataframe)
        except Exception as e:
            raise MyException(e, sys)