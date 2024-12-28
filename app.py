import logging
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from functools import wraps
import os
from dbUtils import get_db, close_db, validate_login, get_user, register_user
from dbUtils import get_merchants_revenue, get_delivery_person_orders, get_customers_due_amount
from dbUtils import add_menu_item, get_menu_item

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 設置數據庫配置
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' #原本為root 但我的DB沒有密碼
app.config['MYSQL_DB'] = 'foodpangolin'
app.config['MYSQL_PORT'] = 3306    #原本為8889 windows環境port為3306

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
                register_user(username, password, int(role))
                flash('Registration successful!', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                app.logger.error(f"Error during registration: {e}")
                errors.append('An error occurred during registration')
        
    return render_template('register.html', errors=errors)


@app.route('/', methods=['GET', 'POST'])     #將此處直接定義為根路由
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
            print("sessionid:",session['user_id'])
            flash('Login successful!', 'success')
            if session['role'] == 1:
                print(f"目前role={session['role']} 商家")
                return render_template('restaurant/rindex.html')
            elif session['role'] == 2:
                print(f"目前role={session['role']} 小哥")
                return render_template('delivery/delivery_index.html')
            elif session['role'] == 3:
                print(f"目前role={session['role']} 客戶")
                return render_template('customer/index.html')
            else:
                return render_template('platform.html') 
        else:
            errors.append('Invalid username or password')
            flash('Invalid username or password', 'danger')
    return render_template('login.html', errors=errors)



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/platform/dashboard')
#@login_required
def platform_dashboard():
    merchants_revenue = get_merchants_revenue()
    delivery_person_orders = get_delivery_person_orders()
    customers_due_amount = get_customers_due_amount()

    #if session.get('role') == 4:
    return render_template('platform.html', 
            merchants_revenue=merchants_revenue, 
            delivery_person_orders=delivery_person_orders, 
            customers_due_amount=customers_due_amount)

#小哥
@app.route('/delivery_index')
def delivery_index():
    return render_template('delivery/delivery_index.html')

@app.route('/view_orders')
def view_order():
    return render_template('delivery/view_orders.html')

@app.route('/accepted_orders')
def accepted_order():
    return render_template('delivery/accepted.html')

@app.route('/completed_orders')
def completed_orders():
    return render_template('delivery/completed_orders.html')

#餐廳
@app.route('/restaurant_index')
def restaurant_index():
    return render_template('restaurant/rindex.html')

@app.route('/menu')
def menu():
    try:
        restaurant_id = session.get('user_id') 
        print(f"從 session 中獲取的 restaurant_id: {restaurant_id}")
        menu_items = get_menu_item(restaurant_id)
        return render_template('restaurant/menu.html', menu_items=menu_items)
    except Exception as e:
        app.logger.error(f"Error rendering menu page: {e}")
        return render_template('restaurant/menu.html', menu_items=[])

@app.route('/orders')
def restaurant_orders():
    return render_template('restaurant/orders.html')

@app.route('/pickup')
def restaurant_pickup():
    return render_template('restaurant/pickup.html')

@app.route('/add_menu_item', methods=['POST'])
def add_menu_item_route():
    try:
        # 接收前端傳來的數據
        data = request.get_json()
        item_name = data.get('item_name')
        price = data.get('price')
        restaurant_id = 1  # 假設 restaurant_id 為 1，可以根據登入用戶設定動態值

        if not item_name or not price:
            return jsonify({'error': '缺少菜品名稱或價格'}), 400

        # 調用 dbUtils 函數插入數據
        add_menu_item(restaurant_id, item_name, price)

        return jsonify({'success': True, 'message': '菜品已成功上架'})
    except Exception as e:
        return jsonify({'error': '菜品上架失敗'}), 500


    
if __name__ == '__main__':
    app.run(debug=True)
