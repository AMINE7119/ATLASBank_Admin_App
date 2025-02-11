from flask import Blueprint, render_template, session
from app.services.analytics_service import AnalyticsService
from app.errors.error import handle_401
from functools import wraps

analytics_bp = Blueprint('analytics', __name__)
analytics_service = AnalyticsService()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_id'):
            return handle_401("Authentication required")
        return f(*args, **kwargs)
    return decorated_function

@analytics_bp.route('/dashboard')
@login_required
def dashboard():
    dashboard_data = analytics_service.generate_dashboard_data()
    return render_template('analytics/dashboard.html', data=dashboard_data)