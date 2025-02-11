import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, Any
from datetime import datetime, timedelta
from app.dal.analytics_dao import AnalyticsDAO

class AnalyticsService:
    def __init__(self):
        self.analytics_dao = AnalyticsDAO()
        self.colors = ['#4e6e6e', '#acbccc', '#0f323b', '#6b888f', '#2c4f59']
        self.background_color = '#ffffff'
        self.text_color = '#0f323b'
        
        plt.style.use('default')
        matplotlib.rcParams.update({
            'text.color': self.text_color,
            'axes.labelcolor': self.text_color,
            'xtick.color': self.text_color,
            'ytick.color': self.text_color,
            'figure.facecolor': self.background_color,
            'axes.facecolor': self.background_color,
            'savefig.facecolor': self.background_color,
            'axes.grid': True,
            'grid.alpha': 0.3,
            'grid.color': '#cccccc',
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10
        })

    def generate_dashboard_data(self) -> Dict[str, Any]:
        try:
            summary = self.analytics_dao.get_accounts_summary()
            trends = self.analytics_dao.get_transaction_trends(days=90)
            demographics = self.analytics_dao.get_user_demographics()
            account_types = self.analytics_dao.get_account_type_distribution()

            # Handle empty datasets
            if not trends:
                trends = [{'trans_date': datetime.now().date(), 'type': 'No Data', 
                          'transaction_count': 0, 'total_amount': 0}]
            if not demographics:
                demographics = [{'gender': 'No Data', 'count': 1, 'avg_age': 0}]
            if not account_types:
                account_types = [{'type': 'No Data', 'count': 1, 'avg_balance': 0}]

            # Transaction Trends
            trends_df = pd.DataFrame(trends)
            fig, ax = plt.subplots(figsize=(12, 6))
            if len(trends) > 1:
                for i, trans_type in enumerate(trends_df['type'].unique()):
                    type_data = trends_df[trends_df['type'] == trans_type]
                    ax.plot(type_data['trans_date'], type_data['total_amount'], 
                           label=trans_type, color=self.colors[i % len(self.colors)],
                           linewidth=2.5, marker='o', markersize=4)
            
            ax.set_title('Transaction Trends (90 Days)', pad=20, fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Amount (MAD)')
            ax.grid(True, linestyle='--', alpha=0.7)
            if len(trends) > 1:
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            trends_img = self._get_plot_image()

            # Demographics
            demo_df = pd.DataFrame(demographics)
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
            
            # Gender distribution
            wedges, texts, autotexts = ax1.pie(demo_df['count'], labels=demo_df['gender'], 
                                              autopct='%1.1f%%', startangle=140, colors=self.colors,
                                              wedgeprops={'edgecolor': 'white', 'linewidth': 2})
            ax1.set_title('Gender Distribution', pad=20, fontweight='bold')

            # Age distribution
            if 'avg_age' in demo_df.columns and demo_df['avg_age'].sum() > 0:
                bars = ax2.bar(demo_df['gender'], demo_df['avg_age'], 
                             color=self.colors[0:len(demo_df)],
                             edgecolor='white', linewidth=2)
                ax2.set_title('Average Age by Gender', pad=20, fontweight='bold')
                ax2.set_ylabel('Age (Years)')
                
                for bar in bars:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1f}',
                            ha='center', va='bottom')
            
            plt.tight_layout()
            demographics_img = self._get_plot_image()

            # Account Types
            account_type_df = pd.DataFrame(account_types)
            fig, ax = plt.subplots(figsize=(10, 10))
            wedges, texts, autotexts = ax.pie(account_type_df['count'], 
                                            labels=account_type_df['type'],
                                            autopct='%1.1f%%',
                                            colors=self.colors,
                                            wedgeprops={'edgecolor': 'white', 'linewidth': 2})
            
            ax.set_title('Account Type Distribution', pad=20, fontweight='bold')
            plt.tight_layout()
            account_type_img = self._get_plot_image()

            # Daily Transaction Volume
            if len(trends) > 1:
                daily_volume = self._calculate_daily_transaction_volume(trends_df)
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(daily_volume.index, daily_volume.values, 
                       color=self.colors[0], linewidth=2.5,
                       marker='o', markersize=4)
                ax.set_title('Daily Transaction Volume', pad=20, fontweight='bold')
                ax.set_xlabel('Date')
                ax.set_ylabel('Number of Transactions')
                ax.grid(True, linestyle='--', alpha=0.7)
            else:
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.text(0.5, 0.5, 'No transaction data available', 
                       ha='center', va='center', fontsize=14)
                ax.set_title('Daily Transaction Volume', pad=20, fontweight='bold')
            plt.tight_layout()
            volume_img = self._get_plot_image()

            return {
                'summary': summary,
                'trends_chart': trends_img,
                'demographics_chart': demographics_img,
                'account_type_chart': account_type_img,
                'volume_chart': volume_img,
                'raw_data': {
                    'trends': trends,
                    'demographics': demographics,
                    'account_types': account_types
                }
            }
        except Exception as e:
            import traceback
            print(f"Error generating dashboard data: {str(e)}")
            print(traceback.format_exc())
            return self._get_error_response()

    def _calculate_daily_transaction_volume(self, trends_df: pd.DataFrame) -> pd.Series:
        """Calculate daily transaction volume across all types"""
        if not trends_df.empty:
            daily_volume = trends_df.groupby('trans_date')['transaction_count'].sum()
            return daily_volume
        return pd.Series()

    def _get_plot_image(self) -> str:
        """Convert matplotlib plot to base64 string"""
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        return base64.b64encode(image_png).decode()

    def _get_error_response(self) -> Dict[str, Any]:
        """Return default error response"""
        return {
            'error': 'Error generating dashboard data',
            'summary': {
                'total_accounts': 0,
                'total_balance': 0,
                'avg_balance': 0,
                'savings_count': 0,
                'checking_count': 0,
                'avg_savings_rate': 0,
                'avg_checking_rate': 0
            }
        }