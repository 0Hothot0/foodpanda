import logging
from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
import os
from dbUtils import get_db, close_db, validate_login, get_user, register_user, get_merchants_revenue, get_delivery_person_orders, get_customers_due_amount

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 設置數據庫配置
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'foodpangolin'
app.config['MYSQL_PORT'] = 8889

# 設置日誌
logging.basicConfig(level=logging.DEBUG)

@app.teardown_appcontext
def teardown_db(exception):
    close_db()

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/', methods=['GET', 'POST']) #登入畫面
def login():
    app.logger.debug('Login route called')
    errors = []
    if request.method == 'POST':
        app.logger.debug('Login form submitted')
        username = request.form['username']
        password = request.form['password']
        user = validate_login(username, password)
        if user:
            session['user_id'] = user['user_id']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return render_template('platform.html')
        else:
            errors.append('Invalid username or password')
            flash('Invalid username or password', 'danger')
    return render_template('login.html', errors=errors)

@app.route('/register', methods=['GET', 'POST'])
def register():
    app.logger.debug('Register route called')
    errors = []
    if request.method == 'POST':
        app.logger.debug('Register form submitted')
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']
        
        if password != confirm_password:
            errors.append('Confirm Password does not match Password')
        if not errors:
            try:
                register_user(username, password, int(role)) # db裡，處理用戶註冊
                flash('Registration successful!', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                app.logger.error(f"Error during registration: {e}")
                errors.append('An error occurred during registration')
        
    return render_template('register.html', errors=errors)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/platform/dashboard')
@login_required
def platform_dashboard():
    merchants_revenue = get_merchants_revenue()
    delivery_person_orders = get_delivery_person_orders()
    customers_due_amount = get_customers_due_amount()

    if session.get('role') == 4:
        return render_template('platform.html', 
            merchants_revenue=merchants_revenue, 
            delivery_person_orders=delivery_person_orders, 
            customers_due_amount=customers_due_amount)
    
if __name__ == '__main__':
    app.run(debug=True)
