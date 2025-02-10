from flask import Blueprint, render_template
from app.services.analytics_service import AnalyticsService
from functools import wraps
from flask import session
from werkzeug.exceptions import Unauthorized

analytics_bp = Blueprint('analytics', __name__)
analytics_service = AnalyticsService()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_id'):
            raise Unauthorized("Authentication required")
        return f(*args, **kwargs)
    return decorated_function

@analytics_bp.route('/dashboard')
@login_required
def dashboard():
    """Display analytics dashboard"""
    dashboard_data = analytics_service.generate_dashboard_data()
    return render_template('analytics/dashboard.html', data=dashboard_data)