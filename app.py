import logging
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from functools import wraps
import os
from dbUtils import get_db, close_db, validate_login, get_user, register_user,get_completed_order
from dbUtils import get_merchants_revenue, get_delivery_person_orders, get_customers_due_amount
from dbUtils import add_menu_item, get_menu_item, get_pending_order, get_order_detail, get_accepted_order
from dbUtils import get_menu, get_all_restaurants, get_order_details

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
    pending_orders = get_pending_order()
    return render_template('delivery/view_orders.html', order = pending_orders)

@app.route('/accepted_orders/')
def accepted_order():
    accepted_orders = get_accepted_order()
    return render_template('delivery/accepted.html',order = accepted_orders)

@app.route('/completed_orders')
def completed_order():
    completed_orders = get_completed_order()
    return render_template('delivery/completed_orders.html',order = completed_orders)

@app.route('/order/<int:order_id>')
def order_detail(order_id):
    order_detail = get_order_detail(order_id)
    print(order_detail)
    return render_template('delivery/orderdetail.html', order=order_detail)


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

#客戶
@app.route('/customer_index')
def customer_index():
    return render_template('customer/index.html')

@app.route('/merchant.html', methods=['GET'])
@login_required  # 確保只有已登入的客戶才能訪問
def merchants():
    """
    顯示所有商家的列表頁面
    """
    try:
        # 調用DB函數獲取所有商家
        merchants = get_all_restaurants()
        # 渲染商家列表模板，將商家資料傳遞到前端
        return render_template('customer/merchant.html', merchants=merchants)
    except Exception as e:
        app.logger.error(f"Error rendering merchants page: {e}")
        # 如果出現錯誤，回傳空的商家列表頁面
        return render_template('customer/merchant.html', merchants=[])


@app.route('/menu/<int:restaurant_id>', methods=['GET'])
@login_required
def menu_c(restaurant_id):
    """
    顯示指定餐廳的菜單頁面
    """
    try:
        # 調用資料庫函數，獲取指定餐廳的菜單資料
        menu_items = get_menu(restaurant_id)
        # 渲染菜單模板，將菜單資料傳遞到前端
        return render_template('customer/menu_c.html', menu_items=menu_items, restaurant_id=restaurant_id)
    except Exception as e:
        app.logger.error(f"Error rendering menu for restaurant_id {restaurant_id}: {e}")
        # 如果出現錯誤，返回空的菜單頁面
        return render_template('customer/menu_c.html', menu_items=[], restaurant_id=restaurant_id)

@app.route('/order_status.html', methods=['GET'])
@login_required
def order_status():
    """
    顯示客戶的訂單狀態頁面
    """
    try:
        # 從 session 中獲取客戶 ID
        customer_id = session.get('user_id')
        if not customer_id:
            return redirect(url_for('login'))

        # 獲取該客戶的所有訂單
        orders = get_order_details(customer_id)

        # 傳遞訂單資料到前端模板
        return render_template('order_status.html', orders=orders)
    except Exception as e:
        app.logger.error(f"Error fetching order status: {e}")
        return render_template('order_status.html', orders=[])

    
if __name__ == '__main__':
    app.run(debug=True)
