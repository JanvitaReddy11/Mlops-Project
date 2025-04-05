import sys

from src.cloud_storage.gcs_storage import GoogleStorage
from src.exception import MyException
from src.logger import logging
from src.entity.artifact_entity import ModelPusherArtifact, ModelEvaluationArtifact
from src.entity.config_entity import ModelPusherConfig
from src.entity.gcs_estimator import Proj1Estimator


class ModelPusher:
    """
    Handles model pushing to Google Cloud Storage (GCS).
    """

    def __init__(self, model_evaluation_artifact: ModelEvaluationArtifact, model_pusher_config: ModelPusherConfig):
        """
        :param model_evaluation_artifact: Contains trained model path and evaluation details.
        :param model_pusher_config: Configuration for storing the model in GCS.
        """
        self.gcs = GoogleStorage()
        self.model_evaluation_artifact = model_evaluation_artifact
        self.model_pusher_config = model_pusher_config
        self.proj1_estimator = Proj1Estimator(
            storage_name=model_pusher_config.storage_name,  # Fixed parameter name
            model_path=model_pusher_config.gcs_model_key_path
        )

    def initiate_model_pusher(self) -> ModelPusherArtifact:
        """
        Uploads the trained model to Google Cloud Storage and returns an artifact with details.
        """
        logging.info("Starting model push process...")

        try:
            logging.info("Uploading trained model to GCS bucket...")
            self.proj1_estimator.save_model(from_file=self.model_evaluation_artifact.trained_model_path)
            
            model_pusher_artifact = ModelPusherArtifact(
                storage_name=self.model_pusher_config.storage_name,
                gcs_model_path=self.model_pusher_config.gcs_model_key_path
            )

            logging.info("Model successfully uploaded to GCS bucket.")
            logging.info(f"Model Pusher Artifact: {model_pusher_artifact}")
            logging.info("Exited initiate_model_pusher method of ModelPusher class.")

            return model_pusher_artifact

        except Exception as e:
            logging.error("Error occurred while pushing model to GCS.", exc_info=True)
            raise MyException(e, sys) from e