import logging
import sys
import os
from datetime import datetime

LOG_DIR = 'logs'
LOG_FILE = f"{datetime.now().strftime('%Y_%m_%d')}_app.log"  # Better format for daily logs

def setup_logging(log_dir=LOG_DIR, log_file=LOG_FILE):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file_path = os.path.join(log_dir, log_file)
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),  
            logging.FileHandler(log_file_path, mode='a')  ]
    )
    
    logging.info("Logging setup complete.")

setup_logging()
