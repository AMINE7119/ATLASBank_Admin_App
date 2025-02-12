import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from decimal import Decimal
from datetime import datetime, timedelta
import io
import base64
from typing import Dict, Any, Optional, List
from app.dal.analytics_dao import AnalyticsDAO

class AnalyticsService:
    def __init__(self):
        self.analytics_dao = AnalyticsDAO()
        self.setup_style()

    def setup_style(self):
        """Setup matplotlib style configuration"""
        self.colors = ['#4e6e6e', '#acbccc', '#0f323b', '#6b888f', '#2c4f59']
        self.background_color = '#ffffff'
        self.text_color = '#0f323b'
        self.figure_size = (12, 6)
        
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
            # Fetch all data
            summary = self.analytics_dao.get_accounts_summary()
            trends = self.analytics_dao.get_transaction_trends(days=90)
            demographics = self.analytics_dao.get_user_demographics()
            account_types = self.analytics_dao.get_account_type_distribution()
            monthly_growth = self.analytics_dao.get_monthly_growth()

            # Convert data to DataFrames for analysis
            trends_df = pd.DataFrame(trends) if trends else pd.DataFrame()
            if not trends_df.empty:
                trends_df['total_amount'] = trends_df['total_amount'].astype(float)
                trends_df['avg_amount'] = trends_df['avg_amount'].astype(float)

            # Calculate metrics
            metrics = self._calculate_metrics(trends_df, demographics, account_types, monthly_growth)

            # Generate charts
            charts = {
                'trends_chart': self._generate_trends_chart(trends_df),
                'volume_chart': self._generate_volume_chart(trends_df),
                'demographics_chart': self._generate_demographics_chart(demographics),
                'account_type_chart': self._generate_account_type_chart(account_types),
                'growth_chart': self._generate_growth_chart(monthly_growth)
            }

            return {
                'summary': summary,
                'metrics': metrics,
                **charts
            }

        except Exception as e:
            import traceback
            print(f"Error generating dashboard data: {str(e)}")
            print(traceback.format_exc())
            return self._get_error_response()

    def _calculate_metrics(self, trends_df: pd.DataFrame, demographics: List[Dict], 
                         account_types: List[Dict], monthly_growth: List[Dict]) -> Dict[str, Dict]:
        return {
            'transaction_metrics': self._calculate_transaction_metrics(trends_df),
            'user_metrics': self._calculate_user_metrics(demographics),
            'account_metrics': self._calculate_account_metrics(account_types),
            'growth_metrics': self._calculate_growth_metrics(monthly_growth)
        }

    def _calculate_transaction_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        if df.empty:
            return {
                'total_volume': 0,
                'total_volume_90days': 0,
                'avg_transaction_size': 0,
                'max_daily_volume': 0,
                'transaction_growth': 0
            }

        return {
            'total_volume': float(df['total_amount'].sum()),
            'total_volume_90days': float(df['total_amount'].sum()),
            'avg_transaction_size': float(df['avg_amount'].mean()),
            'max_daily_volume': int(df.groupby('trans_date')['transaction_count'].sum().max()),
            'transaction_growth': float(df.groupby('trans_date')['transaction_count'].sum().pct_change().mean() * 100)
        }

    def _calculate_user_metrics(self, demographics: List[Dict]) -> Dict[str, Any]:
        if not demographics:
            return {
                'total_users': 0,
                'active_users': 0,
                'inactive_users': 0,
                'avg_user_age': 0,
                'total_unique_jobs': 0
            }

        df = pd.DataFrame(demographics)
        return {
            'total_users': int(df['count'].sum()),
            'active_users': int(df['active_users'].sum()),
            'inactive_users': int(df['inactive_users'].sum()),
            'avg_user_age': float(df['avg_age'].mean()),
            'total_unique_jobs': int(df['unique_jobs'].sum())
        }

    def _calculate_account_metrics(self, account_types: List[Dict]) -> Dict[str, Any]:
        if not account_types:
            return {
                'total_active_accounts': 0,
                'total_inactive_accounts': 0,
                'avg_balance_active': 0,
                'highest_balance_type': 'N/A'
            }

        df = pd.DataFrame(account_types)
        return {
            'total_active_accounts': int(df['active_accounts'].sum()),
            'total_inactive_accounts': int(df['inactive_accounts'].sum()),
            'avg_balance_active': float(df['avg_active_balance'].mean()),
            'highest_balance_type': df.loc[df['avg_balance'].idxmax(), 'type'] if not df.empty else 'N/A'
        }

    def _calculate_growth_metrics(self, monthly_growth: List[Dict]) -> Dict[str, float]:
        if not monthly_growth:
            return {
                'avg_monthly_growth': 0,
                'latest_growth': 0,
                'active_accounts_trend': 0
            }

        df = pd.DataFrame(monthly_growth)
        return {
            'avg_monthly_growth': float(df['growth_rate'].mean()),
            'latest_growth': float(df['growth_rate'].iloc[-1]) if not df.empty else 0,
            'active_accounts_trend': float(df['active_accounts'].pct_change().mean() * 100)
        }

    def _generate_trends_chart(self, df: pd.DataFrame) -> str:
        if df.empty:
            return self._get_empty_chart("No Transaction Data Available")

        fig, ax = plt.subplots(figsize=self.figure_size)
        
        for i, trans_type in enumerate(df['type'].unique()):
            type_data = df[df['type'] == trans_type]
            dates = pd.to_datetime(type_data['trans_date'])
            amounts = type_data['total_amount'].values

            # Plot actual data
            ax.plot(dates, amounts, label=trans_type,
                   color=self.colors[i % len(self.colors)],
                   linewidth=2.5, marker='o', markersize=4)

            # Add trend line
            if len(dates) > 1:
                x = np.arange(len(dates))
                z = np.polyfit(x, amounts, 1)
                p = np.poly1d(z)
                ax.plot(dates, p(x), linestyle='--',
                       color=self.colors[i % len(self.colors)],
                       alpha=0.5, label=f'{trans_type} Trend')

        ax.set_title('Transaction Trends (90 Days)', pad=20, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Amount (MAD)')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        return self._get_plot_image()

    def _generate_volume_chart(self, df: pd.DataFrame) -> str:
        if df.empty:
            return self._get_empty_chart("No Volume Data Available")

        daily_volume = df.groupby('trans_date')['transaction_count'].sum()
        rolling_avg = daily_volume.rolling(window=7, min_periods=1).mean()

        fig, ax = plt.subplots(figsize=self.figure_size)
        ax.plot(daily_volume.index, daily_volume.values,
               color=self.colors[0], linewidth=2.5,
               marker='o', markersize=4, label='Daily Volume')
        ax.plot(rolling_avg.index, rolling_avg.values,
               color=self.colors[1], linewidth=2,
               linestyle='--', label='7-Day Average')

        ax.set_title('Daily Transaction Volume', pad=20, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Transactions')
        ax.legend()
        plt.tight_layout()
        return self._get_plot_image()

    def _generate_demographics_chart(self, demographics: List[Dict]) -> str:
        if not demographics:
            return self._get_empty_chart("No Demographics Data Available")

        df = pd.DataFrame(demographics)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
        
        # Gender distribution
        ax1.pie(df['count'], labels=df['gender'],
                autopct='%1.1f%%', startangle=140,
                colors=self.colors[:len(df)],
                wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        ax1.set_title('Gender Distribution', pad=20, fontweight='bold')

        # Age distribution
        bars = ax2.bar(df['gender'], df['avg_age'],
                      color=self.colors[:len(df)],
                      edgecolor='white', linewidth=2)
        ax2.set_title('Age Demographics', pad=20, fontweight='bold')
        ax2.set_ylabel('Age (Years)')

        # Add age range annotations
        for i, row in df.iterrows():
            ax2.text(i, row['avg_age'] + 1,
                    f'Range: {int(row["min_age"])}-{int(row["max_age"])}',
                    ha='center', va='bottom')

        plt.tight_layout()
        return self._get_plot_image()

    def _generate_account_type_chart(self, account_types: List[Dict]) -> str:
        if not account_types:
            return self._get_empty_chart("No Account Type Data Available")

        df = pd.DataFrame(account_types)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
        
        # Account type distribution
        ax1.pie(df['count'], labels=df['type'],
                autopct='%1.1f%%', colors=self.colors[:len(df)],
                wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        ax1.set_title('Account Type Distribution', pad=20, fontweight='bold')

        # Balance distribution
        bars = ax2.bar(df['type'], df['avg_balance'],
                      color=self.colors[:len(df)],
                      edgecolor='white', linewidth=2)
        ax2.set_title('Average Balance by Type', pad=20, fontweight='bold')
        ax2.set_ylabel('Balance (MAD)')

        # Add balance annotations
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'MAD{height:,.0f}',
                    ha='center', va='bottom')

        plt.tight_layout()
        return self._get_plot_image()

    def _generate_growth_chart(self, monthly_growth: List[Dict]) -> str:
        if not monthly_growth:
            return self._get_empty_chart("No Growth Data Available")

        df = pd.DataFrame(monthly_growth)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
        
        # Monthly growth rate
        ax1.plot(df['month'], df['growth_rate'],
                color=self.colors[0], marker='o',
                linewidth=2, label='Growth Rate')
        ax1.set_title('Monthly Growth Rate', pad=20, fontweight='bold')
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Growth Rate (%)')
        ax1.tick_params(axis='x', rotation=45)

        # Active accounts trend
        ax2.plot(df['month'], df['active_accounts'],
                color=self.colors[1], marker='o',
                linewidth=2, label='Active Accounts')
        ax2.set_title('Active Accounts Trend', pad=20, fontweight='bold')
        ax2.set_xlabel('Month')
        ax2.set_ylabel('Number of Active Accounts')
        ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        return self._get_plot_image()

    def _get_empty_chart(self, message: str) -> str:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, message,
                ha='center', va='center',
                fontsize=14, color=self.text_color)
        ax.set_axis_off()
        return self._get_plot_image()

    def _get_plot_image(self) -> str:
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close('all')
        return base64.b64encode(image_png).decode()

    def _get_error_response(self) -> Dict[str, Any]:
        return {
            'error': 'Error generating dashboard data',
            'summary': {
                'total_accounts': 0,
                'total_balance': 0,
                'avg_balance': 0,
                'savings_count': 0,
                'checking_count': 0,
                'avg_savings_rate': 0,
                'avg_checking_rate': 0,
                'min_balance': 0,
                'max_balance': 0,
                'inactive_accounts': 0
            },
            'metrics': {
                'transaction_metrics': {
                    'total_volume': 0,
                    'total_volume_90days': 0,
                    'avg_transaction_size': 0,
                    'max_daily_volume': 0,
                    'transaction_growth': 0
                },
                'user_metrics': {
                    'total_users': 0,
                    'active_users': 0,
                    'inactive_users': 0,
                    'avg_user_age': 0,
                    'total_unique_jobs': 0
                },
                'account_metrics': {
                    'total_active_accounts': 0,
                    'total_inactive_accounts': 0,
                    'avg_balance_active': 0,
                    'highest_balance_type': 'N/A'
                },
                'growth_metrics': {
                    'avg_monthly_growth': 0,
                    'latest_growth': 0,
                    'active_accounts_trend': 0
                }
            },
            'trends_chart': self._get_empty_chart("No Data Available"),
            'volume_chart': self._get_empty_chart("No Data Available"),
            'demographics_chart': self._get_empty_chart("No Data Available"),
            'account_type_chart': self._get_empty_chart("No Data Available"),
            'growth_chart': self._get_empty_chart("No Data Available")
        }