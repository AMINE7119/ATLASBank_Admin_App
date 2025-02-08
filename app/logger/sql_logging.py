import logging
import os
from datetime import datetime

def setup_sql_logging():
    # Resolve the log directory path
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_filename = os.path.join(log_dir, 'sql.log')
    
    sql_logger = logging.getLogger('sql')
    sql_logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - SQL - %(levelname)s - Query: %(message)s')
    
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    # Clear existing handlers to avoid duplicate logging
    for handler in sql_logger.handlers[:]:
        sql_logger.removeHandler(handler)
    
    sql_logger.addHandler(file_handler)
    sql_logger.addHandler(stream_handler)
    
    return sql_logger