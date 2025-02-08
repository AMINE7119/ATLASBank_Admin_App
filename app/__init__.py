from flask import Flask, render_template
from app.controllers.auth_controller import auth_bp
from app.controllers.bank_controller import bank_bp
from app.errors.error import register_error_handlers
import secrets

def create_app():
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(32)

    app.register_blueprint(auth_bp)
    app.register_blueprint(bank_bp, url_prefix='/bank')
    register_error_handlers(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app