'''from src.logger import logging
from src.exception import MyException
import sys

try:
     a = 1+'Z'
except Exception as e:
     logging.error(e)
     raise MyException(e, sys) from e'''

from src.pipline.training_pipeline import TrainPipeline

pipeline = TrainPipeline()
pipeline.run_pipeline()