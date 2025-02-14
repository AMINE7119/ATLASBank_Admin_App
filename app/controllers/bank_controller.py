from flask import Blueprint, render_template, session, redirect, url_for, request, flash, abort
from app.services.bank_service import BankService
from app.logger.app_logging import setup_logging
from functools import wraps
from decimal import Decimal, InvalidOperation
from datetime import datetime
from app.errors.error import NotFound, handle_401, handle_404, handle_500

logger = setup_logging()
bank_bp = Blueprint('bank', __name__)
bank_service = BankService()

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_id'):
            logger.warning("Unauthorized access attempt")
            return handle_401("Authentication required")
        return f(*args, **kwargs)
    return decorated_function

@bank_bp.route('/menu')
@auth_required
def menu():
    return render_template('bank/menu.html')

@bank_bp.route('/list')
@auth_required
def list():
    try:
        accounts = bank_service.list_accounts()
        return render_template('bank/list.html', accounts=accounts)
    except Exception as e:
        logger.error(f"Error listing accounts: {str(e)}")
        return handle_500(e)

@bank_bp.route('/view/<int:account_number>')
@auth_required
def view(account_number):
    try:
        account = bank_service.get_account(account_number)
        return render_template('bank/view.html', account=account)
    except NotFound:
        return handle_404(f"Account {account_number} not found")
    except Exception as e:
        logger.error(f"Error viewing account {account_number}: {str(e)}")
        return handle_500(e)

@bank_bp.route('/edit/<int:account_number>', methods=['GET', 'POST'])
@auth_required
def edit(account_number):
    try:
        if request.method == 'POST':
            data = {
                'type': request.form.get('type'),
                'balance': request.form.get('balance'),
                'status': request.form.get('status') == 'true',
                'interest_rate': request.form.get('interest_rate', '0.00')
            }
            
            account = bank_service.update_account(account_number, data)
            flash('Account updated successfully', 'success')
            return redirect(url_for('bank.view', account_number=account_number))
            
        account = bank_service.get_account(account_number)
        return render_template('bank/edit.html', account=account)
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('bank.view', account_number=account_number))
    except NotFound:
        return handle_404(f"Account {account_number} not found")
    except Exception as e:
        logger.error(f"Error editing account {account_number}: {str(e)}")
        return handle_500(e)

@bank_bp.route('/create', methods=['GET', 'POST'])
@auth_required
def create():
    if request.method == 'POST':
        try:
            data = {
                'first_name': request.form.get('first_name'),
                'last_name': request.form.get('last_name'),
                'email': request.form.get('email'),
                'phone': request.form.get('phone'),
                'address': request.form.get('address'),
                'date_of_birth': request.form.get('date_of_birth'),
                'gender': request.form.get('gender'),
                'job': request.form.get('job'),
                'type': request.form.get('type'),
                'balance': request.form.get('balance', '0'),
                'interest_rate': request.form.get('interest_rate', '0')
            }
            
            logger.info(f"Attempting to create account with data: {data}")
            account = bank_service.create_account(data)
            
            if not account:
                raise ValueError("Account creation failed - no account returned")
                
            if not hasattr(account, 'account_number'):
                raise ValueError("Account creation failed - invalid account object")
                
            logger.info(f"Successfully created account number: {account.account_number}")
            flash('Account created successfully!', 'success')
            
            logger.info(f"Redirecting to view page for account: {account.account_number}")
            return redirect(url_for('bank.view', account_number=account.account_number))

        except ValueError as e:
            logger.warning(f"Validation error in create: {str(e)}")
            flash(str(e), 'error')
            return render_template('bank/create.html', data=data)
            
        except Exception as e:
            logger.error(f"Unexpected error in create: {str(e)}")
            flash("An unexpected error occurred while creating the account", 'error')
            return render_template('errors/500.html'), 500

    return render_template('bank/create.html')
@bank_bp.route('/delete/<int:account_number>', methods=['POST'])
@auth_required
def delete(account_number):
    try:
        bank_service.delete_account(account_number)
        flash('Account deleted successfully', 'success')
        return redirect(url_for('bank.list'))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('bank.view', account_number=account_number))
    except NotFound:
        return handle_404(f"Account {account_number} not found")
    except Exception as e:
        logger.error(f"Error deleting account {account_number}: {str(e)}")
        return handle_500(e)

@bank_bp.route('/search', methods=['GET', 'POST'])
@auth_required
def search():
    action = request.args.get('action')
    
    if request.method == 'POST':
        try:
            search_term = request.form.get('search_term', '').strip()
            if not search_term:
                flash("Please enter a search term", 'warning')
                return render_template('bank/search.html', action=action)
                
            accounts = bank_service.search_accounts(search_term)
            
            if not accounts:
                flash(f"No accounts found for: {search_term}", 'info')
                return render_template('bank/search.html', action=action)
                
            if len(accounts) == 1:
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
            
            return render_template('bank/search.html', accounts=accounts, search_term=search_term, action=action)
            
        except ValueError as e:
            flash(str(e), 'warning')
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            flash("An error occurred during search", 'error')
    
    return render_template('bank/search.html', action=action)

@bank_bp.route('/account/<int:account_number>/deposit', methods=['GET', 'POST'])
@auth_required
def deposit(account_number):
    try:
        account = bank_service.get_account(account_number)
        
        if request.method == 'POST':
            amount = Decimal(request.form.get('amount', '0'))
            description = request.form.get('description')
            
            bank_service.process_deposit(account_number, amount, description)
            flash('Deposit processed successfully', 'success')
            return redirect(url_for('bank.view', account_number=account_number))
            
        return render_template('bank/deposit.html', account=account)
        
    except ValueError as e:
        flash(str(e), 'error')
        return render_template('bank/deposit.html', account=account)
    except NotFound:
        return handle_404(f"Account {account_number} not found")
    except Exception as e:
        logger.error(f"Error processing deposit: {str(e)}")
        return handle_500(e)

@bank_bp.route('/account/<int:account_number>/withdraw', methods=['GET', 'POST'])
@auth_required
def withdraw(account_number):
    try:
        account = bank_service.get_account(account_number)
        
        if request.method == 'POST':
            amount = Decimal(request.form.get('amount', '0'))
            description = request.form.get('description')
            
            bank_service.process_withdrawal(account_number, amount, description)
            flash('Withdrawal processed successfully', 'success')
            return redirect(url_for('bank.view', account_number=account_number))
            
        return render_template('bank/withdraw.html', account=account)
        
    except ValueError as e:
        flash(str(e), 'error')
        return render_template('bank/withdraw.html', account=account)
    except NotFound:
        return handle_404(f"Account {account_number} not found")
    except Exception as e:
        logger.error(f"Error processing withdrawal: {str(e)}")
        return handle_500(e)

@bank_bp.route('/account/<int:account_number>/transfer', methods=['GET', 'POST'])
@auth_required
def transfer(account_number):
    try:
        from_account = bank_service.get_account(account_number)
        
        if request.method == 'POST':
            to_account_number = int(request.form.get('to_account'))
            amount = Decimal(request.form.get('amount', '0'))
            description = request.form.get('description')
            
            bank_service.process_transfer(account_number, to_account_number, amount, description)
            flash('Transfer processed successfully', 'success')
            return redirect(url_for('bank.view', account_number=account_number))
            
        return render_template('bank/transfer.html', account=from_account)
        
    except ValueError as e:
        flash(str(e), 'error')
        return render_template('bank/transfer.html', account=from_account)
    except NotFound:
        return handle_404(f"Account {account_number} not found")
    except Exception as e:
        logger.error(f"Error processing transfer: {str(e)}")
        return handle_500(e)

@bank_bp.route('/account/<int:account_number>/statement', methods=['GET', 'POST'])
@auth_required
def statement(account_number):
    try:
        start_date = request.form.get('start_date') if request.method == 'POST' else request.args.get('start_date')
        end_date = request.form.get('end_date') if request.method == 'POST' else request.args.get('end_date')

        statement = bank_service.get_bank_statement(account_number, start_date, end_date)
        return render_template('bank/statement.html', statement=statement)
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('bank.view', account_number=account_number))
    except NotFound:
        return handle_404(f"Account {account_number} not found")
    except Exception as e:
        logger.error(f"Error generating statement: {str(e)}")
        return handle_500(e)

@bank_bp.route('/errors/<error_code>')
@auth_required
def test_error(error_code):
    try:
        error_code = int(error_code)
        abort(error_code)
    except ValueError:
        abort(404)