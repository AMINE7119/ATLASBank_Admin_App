# app/controllers/bank_controller.py
from flask import Blueprint, render_template, session, redirect, url_for, request
from app.services.bank_service import BankService
from app.logger.app_logging import setup_logging
from functools import wraps

logger = setup_logging()
bank_bp = Blueprint('bank', __name__)
bank_service = BankService()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return bank_service.check_auth(f, *args, **kwargs)
    return decorated_function

@bank_bp.route('/menu')
@login_required
def menu():
    return render_template('bank/menu.html')

@bank_bp.route('/list')
@login_required
def list():
    accounts = bank_service.list_accounts()
    return render_template('bank/list.html', accounts=accounts)

@bank_bp.route('/view/<int:account_number>')
@login_required
def view(account_number):
    account = bank_service.get_account(account_number)
    return render_template('bank/view.html', account=account)

@bank_bp.route('/edit/<int:account_number>', methods=['GET', 'POST'])
@login_required
def edit(account_number):
    if request.method == 'POST':
        data = request.form
        account = bank_service.update_account(account_number, data)
    else:
        account = bank_service.get_account(account_number)
    return render_template('bank/edit.html', account=account)

@bank_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        data = request.form
        account = bank_service.create_account(data)
        return redirect(url_for('bank.view', account_number=account.account_number))
    return render_template('bank/create.html')

@bank_bp.route('/delete/<int:account_number>', methods=['POST'])
@login_required
def delete(account_number):
    bank_service.delete_account(account_number)
    return redirect(url_for('bank.list'))