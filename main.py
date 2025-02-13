from flask import Flask, render_template, Blueprint
from app.controllers.auth_controller import auth_bp
from app.controllers.bank_controller import bank_bp
from app.controllers.analytics_controller import analytics_bp
from app import app
from app.errors.error import register_error_handlers
import secrets

if __name__ == '__main__':
    auth = app.register_blueprint(auth_bp)
    bank = app.register_blueprint(bank_bp, url_prefix='/bank')
    analytics = app.register_blueprint(analytics_bp, url_prefix='/analytics')
    register_error_handlers(app)
    app.secret_key = secrets.token_hex(32)
    
    @app.route('/')
    def index():
        return render_template('auth/login.html')
        
    app.run(debug=True, host='0.0.0.0', port=5000)