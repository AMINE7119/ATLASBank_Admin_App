# app/controllers/bank_controller.py
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.services.bank_service import BankService
from app.logger.app_logging import setup_logging
from functools import wraps
from app.errors.error import NotFound
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
        try:
            # Retrieve and validate form data
            data = {
                # User data
                'first_name': request.form.get('first_name'),
                'last_name': request.form.get('last_name'),
                'email': request.form.get('email'),
                'phone': request.form.get('phone'),
                'address': request.form.get('address'),
                'date_of_birth': request.form.get('date_of_birth'),
                'gender': request.form.get('gender'),
                'job': request.form.get('job'),
                
                # Account data
                'type': request.form.get('type'),
                'balance': float(request.form.get('balance', 0)),
                'interest_rate': float(request.form.get('interest_rate', 0))
            }
            
            logger.info(f"Creating account with data: {data}")
            account = bank_service.create_account(data)
            if account:
                return redirect(url_for('bank.view', account_number=account.account_number))
            else:
                raise ValueError("Account creation failed")
                
        except Exception as e:
            logger.error(f"Error in create route: {str(e)}")
            flash(f"Error creating account: {str(e)}", 'error')
            return render_template('bank/create.html')
    
    return render_template('bank/create.html')

@bank_bp.route('/delete/<int:account_number>', methods=['POST'])
@login_required
def delete(account_number):
    bank_service.delete_account(account_number)
    return redirect(url_for('bank.list'))

@bank_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    action = request.args.get('action')  # Get the action from URL parameters
    
    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()
        try:
            if not search_term:
                flash("Please enter a search term", 'warning')
                return render_template('bank/search.html', action=action)
                
            accounts = bank_service.search_accounts(search_term)
            
            if not accounts:
                flash(f"No accounts found for: {search_term}", 'info')
                return render_template('bank/search.html', action=action)
                
            if len(accounts) == 1:
                # If only one account found, redirect based on action
                account = accounts[0]
                if action == 'deposit':
                    return redirect(url_for('bank.deposit', account_number=account.account_number))
                elif action == 'withdraw':
                    return redirect(url_for('bank.withdraw', account_number=account.account_number))
                elif action == 'transfer':
                    return redirect(url_for('bank.transfer', account_number=account.account_number))
                elif action == 'statement':
                    return redirect(url_for('bank.statement', account_number=account.account_number))
                else:
                    return redirect(url_for('bank.view', account_number=account.account_number))
            
            # If multiple accounts found, show list with action context
            return render_template('bank/search.html', accounts=accounts, search_term=search_term, action=action)
            
        except ValueError as e:
            logger.warning(f"Invalid search attempt: {str(e)}")
            flash(str(e), 'warning')
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            flash("An error occurred during search", 'error')
    
    return render_template('bank/search.html', action=action)

@bank_bp.route('/account/<int:account_number>/deposit', methods=['GET', 'POST'])
@login_required
def deposit(account_number):
    try:
        account = bank_service.get_account(account_number)
        if request.method == 'POST':
            amount = float(request.form.get('amount', 0))
            description = request.form.get('description')
            
            if bank_service.process_deposit(account_number, amount, description):
                flash('Deposit processed successfully', 'success')
                return redirect(url_for('bank.view', account_number=account_number))
            
        return render_template('bank/deposit.html', account=account)
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('bank.view', account_number=account_number))

@bank_bp.route('/account/<int:account_number>/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw(account_number):
    try:
        account = bank_service.get_account(account_number)
        if request.method == 'POST':
            amount = float(request.form.get('amount', 0))
            description = request.form.get('description')
            
            if bank_service.process_withdrawal(account_number, amount, description):
                flash('Withdrawal processed successfully', 'success')
                return redirect(url_for('bank.view', account_number=account_number))
            
        return render_template('bank/withdraw.html', account=account)
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('bank.view', account_number=account_number))

@bank_bp.route('/account/<int:account_number>/transfer', methods=['GET', 'POST'])
@login_required
def transfer(account_number):
    try:
        from_account = bank_service.get_account(account_number)
        if request.method == 'POST':
            to_account_number = int(request.form.get('to_account'))
            amount = float(request.form.get('amount', 0))
            description = request.form.get('description')
            
            if bank_service.process_transfer(account_number, to_account_number, amount, description):
                flash('Transfer processed successfully', 'success')
                return redirect(url_for('bank.view', account_number=account_number))
            
        return render_template('bank/transfer.html', account=from_account)
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('bank.view', account_number=account_number))

@bank_bp.route('/account/<int:account_number>/statement', methods=['GET', 'POST'])
@login_required
def statement(account_number):
    try:
        if request.method == 'POST':
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
        else:
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')

        statement = bank_service.get_bank_statement(account_number, start_date, end_date)
        return render_template('bank/statement.html', statement=statement)
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('bank.view', account_number=account_number))
    except Exception as e:
        logger.error(f"Error generating statement: {str(e)}")
        flash("Error generating bank statement", 'error')
        return redirect(url_for('bank.view', account_number=account_number))