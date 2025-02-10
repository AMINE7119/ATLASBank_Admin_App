import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, Any
from app.dal.analytics_dao import AnalyticsDAO

class AnalyticsService:
    def __init__(self):
        self.analytics_dao = AnalyticsDAO()

    def generate_dashboard_data(self) -> Dict[str, Any]:
        try:
            """Generate all analytics data for the dashboard"""
            summary = self.analytics_dao.get_accounts_summary()
            trends = self.analytics_dao.get_transaction_trends()
            demographics = self.analytics_dao.get_user_demographics()
            balance_dist = self.analytics_dao.get_balance_distribution()
            account_types = self.analytics_dao.get_account_type_distribution()

            # Create transaction trends chart
            trends_df = pd.DataFrame(trends)
            plt.figure(figsize=(10, 6))
            for trans_type in trends_df['type'].unique():
                type_data = trends_df[trends_df['type'] == trans_type]
                plt.plot(type_data['trans_date'], type_data['total_amount'], label=trans_type)
            plt.title('Transaction Trends')
            plt.xlabel('Date')
            plt.ylabel('Amount')
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            trends_img = self._get_plot_image()

            # Create demographics chart
            demo_df = pd.DataFrame(demographics)
            plt.figure(figsize=(8, 8))
            plt.pie(demo_df['count'], labels=demo_df['gender'], autopct='%1.1f%%', startangle=140)
            plt.title('User Gender Distribution')
            plt.tight_layout()
            
            demographics_img = self._get_plot_image()

            # Create balance distribution chart
            balance_df = pd.DataFrame(balance_dist)
            plt.figure(figsize=(10, 6))
            plt.bar(balance_df['balance_range'], balance_df['account_count'])
            plt.title('Account Balance Distribution')
            plt.xlabel('Balance Range')
            plt.ylabel('Number of Accounts')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            balance_img = self._get_plot_image()

            # Create account type distribution pie chart
            account_type_df = pd.DataFrame(account_types)
            plt.figure(figsize=(8, 8))
            plt.pie(account_type_df['count'], labels=account_type_df['type'], autopct='%1.1f%%', startangle=140)
            plt.title('Account Type Distribution')
            plt.tight_layout()
            
            account_type_img = self._get_plot_image()

            return {
                'summary': summary,
                'trends_chart': trends_img,
                'demographics_chart': demographics_img,
                'balance_chart': balance_img,
                'account_type_chart': account_type_img,
                'raw_data': {
                    'trends': trends,
                    'demographics': demographics,
                    'balance_distribution': balance_dist,
                    'account_types': account_types
                }
            }
        except Exception as e:
            import traceback
            print(f"Error generating dashboard data: {str(e)}")
            print(traceback.format_exc())
            return {
                'error': str(e),
                'summary': {
                    'total_accounts': 0,
                    'total_balance': 0,
                    'avg_balance': 0,
                    'savings_count': 0,
                    'checking_count': 0
                }
            }
        

    def _get_plot_image(self) -> str:
        """Convert matplotlib plot to base64 string"""
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        return base64.b64encode(image_png).decode()