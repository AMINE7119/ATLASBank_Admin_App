from flask import Flask, render_template
from app.controllers.auth_controller import auth_bp
from app.controllers.bank_controller import bank_bp
from app.controllers.analytics_controller import analytics_bp
from app.errors.error import register_error_handlers
import secrets
#11-2
def create_app():
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(32)

    app.register_blueprint(auth_bp)
    app.register_blueprint(bank_bp, url_prefix='/bank')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    register_error_handlers(app)

    @app.route('/')
    def index():
        return render_template('auth/login.html')

    return app