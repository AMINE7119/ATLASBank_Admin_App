import logging  
from flask import Blueprint, request, render_template, session, redirect, url_for
from app.services.auth_service import authenticate_admin
from app.logger.app_logging import setup_logging

logger = setup_logging()
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = authenticate_admin(username, password)
        if admin:
            session['admin_id'] = admin.id
            logger.info(f"Admin {username} logged in successfully")
            return redirect(url_for('bank.menu'))
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            return render_template('auth/login.html', error='Invalid username or password')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    admin_id = session.pop('admin_id', None)
    if admin_id:
        logger.info(f"Admin ID {admin_id} logged out")
    return redirect(url_for('index'))