import logging
import os
from datetime import datetime

def setup_sql_logging():
    # Resolve the log directory path
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_filename = os.path.join(log_dir, 'sql.log')
    
    # Get logger with specific name 'sql_logger'
    sql_logger = logging.getLogger('sql_logger')
    sql_logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - SQL - %(levelname)s - Query: %(message)s')
    
    # Set up file handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)
    
    # Set up stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    # Clear existing handlers
    sql_logger.handlers.clear()
    
    # Add handlers
    sql_logger.addHandler(file_handler)
    sql_logger.addHandler(stream_handler)
    
    return sql_logger

# Ensure sql_logger is defined
sql_logger = setup_sql_logging()