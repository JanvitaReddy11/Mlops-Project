import sys
import pandas as pd
from sklearn.metrics import f1_score
from typing import Optional
from dataclasses import dataclass

from src.entity.config_entity import ModelEvaluationConfig
from src.entity.artifact_entity import ModelTrainerArtifact, DataIngestionArtifact, ModelEvaluationArtifact
from src.exception import MyException
from src.constants import TARGET_COLUMN
from src.logger import logging
from src.utils.main_utils import load_object
from src.entity.gcs_estimator import Proj1Estimator


@dataclass
class EvaluateModelResponse:
    """
    Data class to store the evaluation result of the model.
    """
    trained_model_f1_score: float
    best_model_f1_score: float
    is_model_accepted: bool
    difference: float


class ModelEvaluation:
    """
    Class to handle the evaluation of a trained model.
    """

    def __init__(self, model_eval_config: ModelEvaluationConfig, data_ingestion_artifact: DataIngestionArtifact, model_trainer_artifact: ModelTrainerArtifact):
        """
        :param model_eval_config: Configuration for model evaluation.
        :param data_ingestion_artifact: Artifact containing data paths.
        :param model_trainer_artifact: Artifact containing trained model information.
        """
        try:
            self.model_eval_config = model_eval_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.model_trainer_artifact = model_trainer_artifact
        except Exception as e:
            raise MyException(e, sys) from e

    def get_best_model(self) -> Optional[Proj1Estimator]:
        """
        Check if the best model exists in GCS and return it.
        :return: Proj1Estimator if model exists, None otherwise.
        """
        try:
            storage_name = self.model_eval_config.storage_name
            model_path = self.model_eval_config.gcs_model_key_path
            proj1_estimator = Proj1Estimator(storage_name=storage_name, model_path=model_path)  # Fixed syntax error

            if proj1_estimator.is_model_present(model_path=model_path):
                return proj1_estimator
            return None
        except Exception as e:
            raise MyException(e, sys) from e

    def evaluate_model(self) -> EvaluateModelResponse:
        """
        Evaluates the trained model and compares it with the best available model.
        :return: EvaluateModelResponse with evaluation results.
        """
        try:
            # Load test data
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)
            x, y = test_df.drop(TARGET_COLUMN, axis=1), test_df[TARGET_COLUMN]

            logging.info("Test data loaded and transforming it for prediction...")

            # Load trained model
            trained_model = load_object(file_path=self.model_trainer_artifact.trained_model_file_path)
            logging.info("Trained model loaded.")

            # Get F1 score of the trained model
            trained_model_f1_score = self.model_trainer_artifact.metric_artifact.f1_score
            logging.info(f"Trained model F1 Score: {trained_model_f1_score}")

            # Evaluate best model if available
            best_model_f1_score = None
            best_model = self.get_best_model()
            if best_model is not None:
                logging.info("Evaluating best model for comparison...")
                y_hat_best_model = best_model.predict(x)
                best_model_f1_score = f1_score(y, y_hat_best_model)
                logging.info(f"Best Model F1 Score: {best_model_f1_score}")

            # Calculate whether the new model is accepted
            tmp_best_model_score = 0 if best_model_f1_score is None else best_model_f1_score
            result = EvaluateModelResponse(
                trained_model_f1_score=trained_model_f1_score,
                best_model_f1_score=best_model_f1_score,
                is_model_accepted=trained_model_f1_score > tmp_best_model_score,
                difference=trained_model_f1_score - tmp_best_model_score
            )

            logging.info(f"Model evaluation result: {result}")
            return result

        except Exception as e:
            raise MyException(e, sys) from e

    def initiate_model_evaluation(self) -> ModelEvaluationArtifact:
        """
        Initiates the model evaluation and returns the evaluation artifact.
        :return: ModelEvaluationArtifact with the evaluation results.
        """
        try:
            logging.info("Initialized Model Evaluation Component.")
            evaluate_model_response = self.evaluate_model()

            gcs_model_path = self.model_eval_config.gcs_model_key_path

            # Create and return the ModelEvaluationArtifact
            model_evaluation_artifact = ModelEvaluationArtifact(
                is_model_accepted=evaluate_model_response.is_model_accepted,
                gcs_model_path=gcs_model_path,
                trained_model_path=self.model_trainer_artifact.trained_model_file_path,
                changed_accuracy=evaluate_model_response.difference
            )

            logging.info(f"Model Evaluation Artifact: {model_evaluation_artifact}")
            return model_evaluation_artifact

        except Exception as e:
            raise MyException(e, sys) from e