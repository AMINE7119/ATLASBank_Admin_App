from typing import Dict, List, Any
from datetime import datetime, timedelta
from app.dal.database import get_cursor
from app.logger.sql_logging import setup_sql_logging

class AnalyticsDAO:
    def __init__(self):
        self.sql_logger = setup_sql_logging()

    def get_accounts_summary(self) -> Dict[str, Any]:
        with get_cursor() as cursor:
            query = """
                SELECT 
                    COUNT(*) as total_accounts,
                    SUM(balance) as total_balance,
                    AVG(balance) as avg_balance,
                    COUNT(CASE WHEN type = 'savings' THEN 1 END) as savings_count,
                    COUNT(CASE WHEN type = 'checking' THEN 1 END) as checking_count,
                    AVG(CASE WHEN type = 'savings' THEN interest_rate ELSE NULL END) as avg_savings_rate,
                    AVG(CASE WHEN type = 'checking' THEN interest_rate ELSE NULL END) as avg_checking_rate
                FROM accounts
                WHERE status = true
            """
            self.sql_logger.info(f"Executing query: {query}")
            cursor.execute(query)
            return dict(zip([desc[0] for desc in cursor.description], cursor.fetchone()))

    def get_transaction_trends(self, days: int = 90) -> List[Dict[str, Any]]:
        with get_cursor() as cursor:
            query = """
                SELECT 
                    DATE(date) as trans_date,
                    type,
                    COUNT(*) as transaction_count,
                    SUM(amount) as total_amount
                FROM transactions
                WHERE date >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY DATE(date), type
                ORDER BY trans_date, type
            """
            self.sql_logger.info(f"Executing query: {query} with days: {days}")
            cursor.execute(query, (days,))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_user_demographics(self) -> List[Dict[str, Any]]:
        with get_cursor() as cursor:
            query = """
                SELECT 
                    gender,
                    COUNT(*) as count,
                    ROUND(AVG(EXTRACT(YEAR FROM AGE(NOW(), date_of_birth)))) as avg_age
                FROM users
                WHERE gender IS NOT NULL
                GROUP BY gender
                ORDER BY gender
            """
            self.sql_logger.info(f"Executing query: {query}")
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_account_type_distribution(self) -> List[Dict[str, Any]]:
        with get_cursor() as cursor:
            query = """
                SELECT 
                    type,
                    COUNT(*) as count,
                    ROUND(AVG(balance)::numeric, 2) as avg_balance,
                    ROUND(AVG(interest_rate)::numeric, 2) as avg_interest_rate
                FROM accounts
                WHERE status = true
                GROUP BY type
                ORDER BY type
            """
            self.sql_logger.info(f"Executing query: {query}")
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]