from flask import Blueprint, render_template

bank_bp = Blueprint('bank', __name__)

@bank_bp.route('/menu')
def menu():
    return render_template('bank/menu.html')