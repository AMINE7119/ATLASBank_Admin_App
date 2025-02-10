import logging
from flask import Blueprint, request, render_template, session, redirect, url_for
from werkzeug.exceptions import Unauthorized, Forbidden, abort
from app.services.auth_service import authenticate_admin
from app.logger.app_logging import setup_logging
from functools import wraps
logger = setup_logging()
auth_bp = Blueprint('auth', __name__)

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_id'):
            abort(401)
        return f(*args, **kwargs)
    return decorated_function
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            logger.warning("Login attempt with missing credentials")
            raise Unauthorized("Username and password are required")
            
        admin = authenticate_admin(username, password)
        if admin:
            session['admin_id'] = admin.id
            logger.info(f"Admin {username} logged in successfully")
            return redirect(url_for('bank.menu'))
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            raise Unauthorized("Invalid username or password")
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    admin_id = session.pop('admin_id', None)
    if admin_id:
        logger.info(f"Admin ID {admin_id} logged out")
    return redirect(url_for('index'))