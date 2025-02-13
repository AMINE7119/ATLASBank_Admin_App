import os
from dotenv import load_dotenv
import psycopg2
from contextlib import contextmanager

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

@contextmanager
def get_cursor():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except psycopg2.DatabaseError as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    try:
        with get_cursor() as cursor:
            cursor.execute('SELECT 1')
            print(cursor.fetchone())
        print("bien")
    except Exception as e:
        print(f"no connect {e}")