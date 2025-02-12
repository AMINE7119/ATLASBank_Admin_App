from itertools import groupby
import json
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict, List, Any
from app.dal.database import get_cursor
from app.logger.sql_logging import setup_sql_logging
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.user import User

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
                    AVG(CASE WHEN type = 'checking' THEN interest_rate ELSE NULL END) as avg_checking_rate,
                    MIN(balance) as min_balance,
                    MAX(balance) as max_balance,
                    COUNT(CASE WHEN status = false THEN 1 END) as inactive_accounts
                FROM accounts"""
            self.sql_logger.info(f"Executing query: {query}")
            cursor.execute(query)
            result = dict(zip([desc[0] for desc in cursor.description], cursor.fetchone()))
            
            # Convert Decimal types to float for JSON serialization
            for key in ['total_balance', 'avg_balance', 'min_balance', 'max_balance', 
                       'avg_savings_rate', 'avg_checking_rate']:
                if key in result and result[key] is not None:
                    result[key] = float(result[key])
            
            return result

    def get_accounts_by_type(self) -> List[Account]:
        with get_cursor() as cursor:
            query = """
                SELECT number, user_id, type, balance, status, interest_rate, created_at
                FROM accounts
                WHERE status = true
                ORDER BY type, number"""
            self.sql_logger.info(f"Executing query: {query}")
            cursor.execute(query)
            return [
                Account(
                    account_number=row[0],
                    user_id=row[1],
                    account_type=row[2],
                    balance=row[3],
                    is_active=row[4],
                    interest_rate=row[5] or Decimal('0.00'),
                    created_at=row[6]
                ) for row in cursor.fetchall()
            ]

    def get_transaction_trends(self, days: int = 90) -> List[Dict[str, Any]]:
        with get_cursor() as cursor:
            query = """
                SELECT 
                    t.date as trans_date,
                    t.type,
                    t.amount,
                    t.account_id,
                    t.recipient_account,
                    t.description,
                    a.balance as account_balance
                FROM transactions t
                JOIN accounts a ON t.account_id = a.number
                WHERE t.date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY t.date DESC"""
            self.sql_logger.info(f"Executing query: {query} with days: {days}")
            cursor.execute(query, (days,))
            
            transactions = []
            for row in cursor.fetchall():
                transaction = Transaction(
                    id=0,  # Not needed for analytics
                    account_number=row[3],
                    operation_type=row[1],
                    amount=row[2],
                    recipient_account=row[4],
                    transaction_date=row[0],
                    description=row[5]
                )
                transactions.append({
                    'trans_date': transaction.transaction_date,
                    'type': transaction.operation_type,
                    'amount': float(transaction.amount),
                    'account_id': transaction.account_number,
                    'recipient_account': transaction.recipient_account,
                    'description': transaction.description,
                    'account_balance': float(row[6])
                })
            
            # Group and aggregate the transactions
            results = []
            sorted_transactions = sorted(transactions, key=lambda x: x['trans_date'].date())
            for date, group in groupby(sorted_transactions, key=lambda x: x['trans_date'].date()):
                group_list = list(group)
                by_type = {}
                for t in group_list:
                    if t['type'] not in by_type:
                        by_type[t['type']] = {'count': 0, 'total': 0, 'amounts': []}
                    by_type[t['type']]['count'] += 1
                    by_type[t['type']]['total'] += t['amount']
                    by_type[t['type']]['amounts'].append(t['amount'])
                
                for type_, data in by_type.items():
                    results.append({
                        'trans_date': date,
                        'type': type_,
                        'transaction_count': data['count'],
                        'total_amount': data['total'],
                        'avg_amount': sum(data['amounts']) / len(data['amounts']),
                        'min_amount': min(data['amounts']),
                        'max_amount': max(data['amounts'])
                    })
            
            return results

    def get_user_demographics(self) -> List[Dict[str, Any]]:
        with get_cursor() as cursor:
            query = """
                SELECT 
                    u.id,
                    u.first_name,
                    u.last_name,
                    u.email,
                    u.phone,
                    u.address,
                    u.date_of_birth,
                    u.status,
                    u.gender,
                    u.job,
                    u.created_at
                FROM users u
                WHERE u.gender IS NOT NULL"""
            self.sql_logger.info(f"Executing query: {query}")
            cursor.execute(query)
            
            users = [User(*row) for row in cursor.fetchall()]
            
            # Group users by gender and calculate metrics
            demographics = {}
            for user in users:
                if user.gender not in demographics:
                    demographics[user.gender] = {
                        'count': 0,
                        'active_users': 0,
                        'inactive_users': 0,
                        'ages': [],
                        'jobs': set()
                    }
                
                demo = demographics[user.gender]
                demo['count'] += 1
                if user.status:
                    demo['active_users'] += 1
                else:
                    demo['inactive_users'] += 1
                
                # Convert date to datetime if necessary
                birth_date = user.date_of_birth
                if isinstance(birth_date, date):
                    birth_date = datetime.combine(birth_date, datetime.min.time())
                age = (datetime.now() - birth_date).days / 365.25
                demo['ages'].append(age)
                if user.job:
                    demo['jobs'].add(user.job)
            
            # Convert to list format
            return [
                {
                    'gender': gender,
                    'count': data['count'],
                    'active_users': data['active_users'],
                    'inactive_users': data['inactive_users'],
                    'avg_age': round(sum(data['ages']) / len(data['ages'])) if data['ages'] else 0,
                    'min_age': round(min(data['ages'])) if data['ages'] else 0,
                    'max_age': round(max(data['ages'])) if data['ages'] else 0,
                    'unique_jobs': len(data['jobs'])
                }
                for gender, data in demographics.items()
            ]

    def get_account_type_distribution(self) -> List[Dict[str, Any]]:
        accounts = self.get_accounts_by_type()
        distribution = {}
        
        for account in accounts:
            if account.account_type not in distribution:
                distribution[account.account_type] = {
                    'type': account.account_type,
                    'count': 0,
                    'balances': [],
                    'interest_rates': [],
                    'active_accounts': 0,
                    'inactive_accounts': 0
                }
            
            dist = distribution[account.account_type]
            dist['count'] += 1
            dist['balances'].append(float(account.balance))
            dist['interest_rates'].append(float(account.interest_rate))
            if account.is_active:
                dist['active_accounts'] += 1
            else:
                dist['inactive_accounts'] += 1
        
        return [
            {
                'type': type_,
                'count': data['count'],
                'avg_balance': sum(data['balances']) / len(data['balances']) if data['balances'] else 0,
                'avg_interest_rate': sum(data['interest_rates']) / len(data['interest_rates']) if data['interest_rates'] else 0,
                'min_balance': min(data['balances']) if data['balances'] else 0,
                'max_balance': max(data['balances']) if data['balances'] else 0,
                'active_accounts': data['active_accounts'],
                'inactive_accounts': data['inactive_accounts'],
                'avg_active_balance': sum(data['balances']) / data['active_accounts'] if data['active_accounts'] > 0 else 0
            }
            for type_, data in distribution.items()
        ]

    def get_monthly_growth(self) -> List[Dict[str, Any]]:
        with get_cursor() as cursor:
            query = """
                WITH monthly_stats AS (
                    SELECT 
                        DATE_TRUNC('month', date) as month,
                        COUNT(DISTINCT account_id) as active_accounts,
                        SUM(amount) as total_volume,
                        COUNT(*) as transaction_count
                    FROM transactions
                    WHERE date >= CURRENT_DATE - INTERVAL '12 months'
                    GROUP BY DATE_TRUNC('month', date)
                    ORDER BY month
                )
                SELECT 
                    month,
                    active_accounts,
                    total_volume,
                    transaction_count,
                    LAG(total_volume) OVER (ORDER BY month) as prev_volume,
                    CASE 
                        WHEN LAG(total_volume) OVER (ORDER BY month) > 0 
                        THEN ((total_volume - LAG(total_volume) OVER (ORDER BY month)) / 
                              LAG(total_volume) OVER (ORDER BY month) * 100)
                        ELSE 0 
                    END as growth_rate
                FROM monthly_stats"""
            self.sql_logger.info(f"Executing query: {query}")
            cursor.execute(query)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'month': row[0],
                    'active_accounts': row[1],
                    'total_volume': float(row[2]) if row[2] is not None else 0,
                    'transaction_count': row[3],
                    'prev_volume': float(row[4]) if row[4] is not None else 0,
                    'growth_rate': float(row[5]) if row[5] is not None else 0
                })
            
            return results