from typing import Dict, List, Any
from datetime import datetime, timedelta
from app.dal.database import get_cursor
from app.logger.sql_logging import setup_sql_logging

class AnalyticsDAO:
    def __init__(self):
        self.sql_logger = setup_sql_logging()

    def get_accounts_summary(self) -> Dict[str, Any]:
        """Get summary statistics for all accounts"""
        with get_cursor() as cursor:
            query = """
                SELECT 
                    COUNT(*) as total_accounts,
                    SUM(balance) as total_balance,
                    AVG(balance) as avg_balance,
                    COUNT(CASE WHEN type = 'savings' THEN 1 END) as savings_count,
                    COUNT(CASE WHEN type = 'checking' THEN 1 END) as checking_count
                FROM accounts
                WHERE status = true
            """
            cursor.execute(query)
            return dict(zip([desc[0] for desc in cursor.description], cursor.fetchone()))

    def get_transaction_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get transaction trends for the specified period"""
        with get_cursor() as cursor:
            query = """
                SELECT 
                    DATE(date) as trans_date,
                    type,
                    COUNT(*) as transaction_count,
                    SUM(amount) as total_amount
                FROM transactions
                WHERE date >= NOW() - INTERVAL '%s days'
                GROUP BY DATE(date), type
                ORDER BY trans_date, type
            """
            cursor.execute(query, (days,))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_user_demographics(self) -> Dict[str, Any]:
        """Get user demographic statistics"""
        with get_cursor() as cursor:
            query = """
                SELECT 
                    gender,
                    COUNT(*) as count,
                    AVG(EXTRACT(YEAR FROM AGE(NOW(), date_of_birth))) as avg_age,
                    COUNT(DISTINCT job) as unique_jobs
                FROM users
                GROUP BY gender
            """
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_balance_distribution(self) -> List[Dict[str, float]]:
        """Get account balance distribution"""
        with get_cursor() as cursor:
            query = """
                SELECT 
                    CASE 
                        WHEN balance BETWEEN 0 AND 1000 THEN '0-1k'
                        WHEN balance BETWEEN 1001 AND 5000 THEN '1k-5k'
                        WHEN balance BETWEEN 5001 AND 10000 THEN '5k-10k'
                        WHEN balance BETWEEN 10001 AND 50000 THEN '10k-50k'
                        ELSE '50k+'
                    END as balance_range,
                    COUNT(*) as account_count,
                    AVG(balance) as avg_balance
                FROM accounts
                WHERE status = true
                GROUP BY 1
                ORDER BY 1
            """
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_account_type_distribution(self) -> List[Dict[str, Any]]:
        """Get account type distribution"""
        with get_cursor() as cursor:
            query = """
                SELECT 
                    type,
                    COUNT(*) as count
                FROM accounts
                WHERE status = true
                GROUP BY type
            """
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]