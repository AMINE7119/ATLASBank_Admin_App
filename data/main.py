import sys
import os

# Dynamically add the project root directory to sys.path
current_file_path = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(current_file_path, '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from etl import process_data
from app.dal.database import close_all_connections

def main():
    try:
        users_path = "/c:/Users/AMINE/Desktop/github/ATLASBank_Admin_App/data/datasets/users.csv"
        transactions_path = "/c:/Users/AMINE/Desktop/github/ATLASBank_Admin_App/data/datasets/transactions.csv"
        
        if process_data(users_path, transactions_path):
            print("Data loaded successfully")
        else:
            print("Failed to load data")
    finally:
        close_all_connections()
        print("Database connections closed")

if __name__ == "__main__":
    main()