import logging
import os
from datetime import datetime

def setup_sql_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    log_filename = f'logs/sql.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - SQL - %(levelname)s - Query: %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

if __name__ == "__main__":
    setup_sql_logging()
    logging.info("SQL logging setup successful")
