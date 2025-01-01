import logging
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from functools import wraps
import os
<<<<<<< HEAD
from dbUtils import get_db, close_db, validate_login, get_user, register_user,get_completed_order, complete_current
from dbUtils import get_merchants_revenue, get_delivery_person_orders, get_customers_due_amount, take_order
from dbUtils import add_menu_item, get_menu_item, get_pending_order, get_order_detail, get_accepted_order, accept_current
from dbUtils import get_menu, get_all_restaurants,  create_order, add_order_detail, add_review, get_orders_by_customer, get_customer_id_by_user_id, get_reviews_by_restaurant, get_merchant_by_id

=======
from dbUtils import get_db, close_db, validate_login, get_user, register_user,get_completed_order,get_restaurant_orders
from dbUtils import get_merchants_revenue, get_delivery_person_orders, get_customers_due_amount,get_order_items
from dbUtils import add_menu_item, get_menu_item, get_pending_order, get_order_detail, get_accepted_order
from dbUtils import get_menu, get_all_restaurants, get_order_details, create_order, add_order_detail, update_restaurant_order_status
from dbUtils import update_order_status_meal_completed, get_meal_completed_orders,delete_item_by_name,edit_menu_item
>>>>>>> origin/mi_1/1_1620
app = Flask(__name__)
app.secret_key = os.urandom(24)

# 設置數據庫配置
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' #原本為root 但我的DB沒有密碼
app.config['MYSQL_DB'] = 'foodpangolin'
app.config['MYSQL_PORT'] = 3307    #原本為8889 windows環境port為3306

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
            session['username'] = user['username']
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
    orders = get_accepted_order()
    # print(orders)
    return render_template('delivery/accepted.html',order = orders)

@app.route('/accepted_current/<int:order_id>', methods=['POST'])
def update_status_to_waitpickup(order_id):
    try:
        # 從 session 獲取 user_id
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '未登入用戶，無法更新訂單'}), 401

        # app.logger.debug(f"接收到 order_id: {order_id} session_id: {user_id}")

        # 調用 accept_current 函數
        accept_current(order_id, user_id)

        # app.logger.debug("SQL 執行完畢")
        return jsonify({'message': f'Order #{order_id} accepted successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/take_order/<int:order_id>', methods=['POST'])
def take(order_id):
    try:
        take_order(order_id)
        return jsonify({'message': f'訂單 #{order_id} 狀態已更新為配送中'}), 200
    except Exception as e:
        print(f"取餐操作失敗: {e}")
        return jsonify({'error': '取餐操作失敗，請稍後再試'}), 500

@app.route('/complete_order/<int:order_id>', methods=['POST'])
def complete_now(order_id):
    try:
        complete_current(order_id)
        return jsonify({'message': f'訂單 #{order_id} 已成功完成'}), 200
    except Exception as e:
        print(f"完成訂單失敗: {e}")
        return jsonify({'error': '完成訂單失敗，請稍後再試'}), 500

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
        restaurant_id = session.get('username')
        if not restaurant_id:
            flash("無效的餐廳 ID，請重新登入", "danger")
            return redirect(url_for('login'))

        menu_items = get_menu_item(restaurant_id)
        app.logger.debug(f"餐廳 {restaurant_id} 的菜單：{menu_items}")
        return render_template('restaurant/menu.html', menu_items=menu_items)
    except Exception as e:
        app.logger.error(f"Error rendering menu page: {e}")
        return render_template('restaurant/menu.html', menu_items=[])
    
@app.route('/edit_menu_item', methods=['POST'])
def edit_menu_item_route():
    try:
        data = request.get_json()  # 獲取前端發送的 JSON 數據
        item_name = data.get('item_name')
        new_item_name = data.get('new_item_name')
        new_price = data.get('new_price')
        restaurant_id = session.get('user_id')  # 確保只影響該餐廳

        if not item_name or not new_item_name or new_price is None:
            return jsonify({'success': False, 'message': '請提供完整的更新資訊'}), 400

        # 調用工具函式進行更新
        if edit_menu_item(item_name, new_item_name, new_price, restaurant_id):
            return jsonify({'success': True, 'message': '菜單項目更新成功'})
        else:
            return jsonify({'success': False, 'message': '菜單項目更新失敗，請確認菜品是否存在'}), 400
    except Exception as e:
        print.logger.error(f"編輯菜單項目時發生錯誤: {e}")
        return jsonify({'success': False, 'message': '伺服器錯誤'}), 500



@app.route('/delete_menu_item', methods=['POST'])
def delete_menu_item():
    try:
        data = request.get_json()  # 獲取前端發送的 JSON 數據
        item_name = data.get('item_name')  # 從請求中獲取 item_name
        print(item_name)

        if not item_name:
            return jsonify({'success': False, 'message': '無效的商品名稱'}), 400

        # 執行刪除操作
        result = delete_item_by_name(item_name)

        if result:
            return jsonify({'success': True, 'message': f'商品 "{item_name}" 已成功刪除'})
        else:
            return jsonify({'success': False, 'message': f'商品 "{item_name}" 刪除失敗，可能不存在'}), 400
    except Exception as e:
        current_app.logger.error(f"刪除商品時發生錯誤: {e}")
        return jsonify({'success': False, 'message': '伺服器錯誤'}), 500

#@app.route('/menu')
#def menu():
#    try:
#        restaurant_id = session.get('user_id')
#        if not restaurant_id:
#            flash("無效的餐廳 ID，請重新登入", "danger")
#            return redirect(url_for('login'))
#        
#        menu_items = get_menu_item(restaurant_id)
#        app.logger.debug(f"餐廳 {restaurant_id} 的菜單：{menu_items}")  # 確認獲取的菜單項目
#        return render_template('restaurant/menu.html', menu_items=menu_items)
#    except Exception as e:
#        app.logger.error(f"Error rendering menu page: {e}")
#        return render_template('restaurant/menu.html', menu_items=menu_items)

@app.route('/orders', methods=['GET', 'POST'])
@login_required
def confirm_order():
    restaurant_id = session.get('user_id')  # 假設 session 中 user_id 是餐廳 ID

    if not restaurant_id:
        flash("無效的餐廳 ID", "danger")
        return redirect(url_for('restaurant_index'))

    if request.method == 'POST':
        order_id = request.form.get('order_id')  # 從表單獲取訂單 ID
        if not order_id:
            flash("無效的訂單 ID", "danger")
            return redirect(url_for('confirm_order'))

        # 調用 dbutils 中的函數更新訂單狀態
        if update_restaurant_order_status(order_id, restaurant_id):
            flash(f"訂單 {order_id} 狀態已更新為 delivery_pending", "success")
        else:
            flash(f"訂單 {order_id} 更新失敗，請檢查該訂單是否有效", "danger")

    # 獲取餐廳狀態為 restaurant_pending 的訂單
    orders = get_restaurant_orders(restaurant_id)

    # 查詢每筆訂單的詳細內容
    for order in orders:
        order['details'] = get_order_items(order['order_id'])  # 使用 `get_order_items` 獲取詳細內容

    return render_template('restaurant/orders.html', orders=orders)

#@app.route('/pickup')
#def restaurant_pickup():
#    return render_template('restaurant/pickup.html')
@app.route('/pickup', methods=['GET', 'POST'])
@login_required
def pickup():
    restaurant_id = session.get('user_id')  # 獲取餐廳 ID

    if not restaurant_id:
        flash("無效的餐廳 ID，請重新登入", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        order_id = request.form.get('order_id')  # 從表單獲取訂單 ID
        if not order_id:
            flash("無效的訂單 ID", "danger")
            return redirect(url_for('pickup'))

        # 更新訂單狀態為 wait_pickup
        if update_order_status_meal_completed(order_id, restaurant_id):
            flash(f"訂單 {order_id} 狀態已更新為 wait_pickup，通知小哥取餐成功", "success")
        else:
            flash(f"訂單 {order_id} 更新失敗，請檢查該訂單是否有效", "danger")

    # 獲取狀態為 meal_completed 的訂單
    orders = get_meal_completed_orders(restaurant_id)

    return render_template('restaurant/pickup.html', orders=orders)

@app.route('/add_menu_item', methods=['POST'])
def add_menu_item_route():
    try:
        # 接收前端傳來的數據
        data = request.get_json()
        item_name = data.get('item_name')
        price = data.get('price')
        restaurant_id = 2  # 假設 restaurant_id 為 1，可以根據登入用戶設定動態值

        if not item_name or not price:
            return jsonify({'error': '缺少菜品名稱或價格'}), 400

        # 調用 dbUtils 函數插入數據
        add_menu_item(restaurant_id, item_name, price)

        return jsonify({'success': True, 'message': '菜品已成功上架'})
    except Exception as e:
        return jsonify({'error': '菜品上架失敗'}), 500



#客戶
@login_required  
@app.route('/customer_index')
def customer_index():
    return render_template('customer/index.html')

@app.route('/merchant.html', methods=['GET'])

def merchants():
    """
    顯示所有商家的列表頁面
    """
    try:
        merchants = get_all_restaurants()
        return render_template('customer/merchant.html', merchants=merchants)
    except Exception as e:
        app.logger.error(f"Error rendering merchants page: {e}")
        return render_template('customer/merchant.html', merchants=[])


@app.route('/menu/<int:restaurant_id>', methods=['GET'])
@login_required
def menu_c(restaurant_id):
    """
    顯示指定餐廳的菜單頁面，並顯示當前客戶的訂單狀態。
    """
    try:
        # 獲取菜單
        menu_items = get_menu(restaurant_id)
        
        # 獲取當前客戶的訂單
        user_id = session.get('user_id')
        customer_id = get_customer_id_by_user_id(user_id)
        if not customer_id:
            app.logger.error("無法獲取客戶 ID")
            return redirect(url_for('login'))
        
        orders = get_orders_by_customer(customer_id)
        
        return render_template('customer/menu_c.html', menu_items=menu_items, restaurant_id=restaurant_id, orders=orders)
    except Exception as e:
        app.logger.error(f"Error rendering menu for restaurant_id {restaurant_id}: {e}")
        return render_template('customer/menu_c.html', menu_items=[], restaurant_id=restaurant_id, orders=[])

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    """
    接收前端傳來的下單請求並存入資料庫。
    """
    try:
        data = request.json
        app.logger.info(f"接收到的數據: {data}")

        order_items = data.get('order_items')
        if not order_items or not isinstance(order_items, list):
            return jsonify({'success': False, 'error': 'Invalid order_items format'}), 400

        # 获取用户信息
        user_id = session.get('user_id')
        customer_id = get_customer_id_by_user_id(user_id)
        if not customer_id:
            return jsonify({'success': False, 'error': '無法確認客戶 ID'}), 400

        # 提取餐廳 ID
        restaurant_id = order_items[0].get('restaurant_id')

        # 创建订单主表
        total_amount = sum(
            get_menu_item(item['menu_id'])['price'] * item['quantity']
            for item in order_items
        )
        order_id = create_order(customer_id, restaurant_id, total_amount)

        # 插入订单详情
        for item in order_items:
            menu_id = item.get('menu_id')
            quantity = item.get('quantity')
            app.logger.debug(f"Inserting into order_details: menu_id={menu_id}, quantity={quantity}")
            add_order_detail(order_id, menu_id, quantity)

        return jsonify({'success': True, 'order_id': order_id})
    except Exception as e:
        app.logger.error(f"下單時發生錯誤: {e}")
        return jsonify({'success': False, 'error': '系統錯誤，請稍後再試'}), 500



    
@app.route('/get_orders', methods=['GET'])
@login_required
def get_orders():
    """
    API 路由：返回客戶的訂單數據
    """
    try:
        # 從 session 中獲取用戶 ID 並獲取客戶 ID
        user_id = session.get('user_id')
        customer_id = get_customer_id_by_user_id(user_id)
        if not customer_id:
            return jsonify({'success': False, 'error': '無法確認客戶身份'}), 401

        # 獲取客戶的訂單
        orders = get_orders_by_customer(customer_id)

        # 返回訂單資料
        return jsonify({'success': True, 'orders': orders})
    except Exception as e:
        app.logger.error(f"Error fetching orders: {e}")
        return jsonify({'success': False, 'error': '系統錯誤，請稍後再試'}), 500


@app.route('/order_status.html', methods=['GET'])
@login_required
def order_status():
    """
    顯示客戶的訂單狀態頁面
    """
    try:
        # 從 session 中獲取用戶 ID 並獲取客戶 ID
        user_id = session.get('user_id')
        customer_id = get_customer_id_by_user_id(user_id)
        if not customer_id:
            return redirect(url_for('login'))

        # 獲取客戶的訂單
        orders = get_orders_by_customer(customer_id)

        # 傳遞訂單資料到前端模板
        return render_template('customer/order_status.html', orders=orders)
    except Exception as e:
        app.logger.error(f"Error fetching order status: {e}")
        return render_template('customer/order_status.html', orders=[])

@app.route('/confirm_receipt/<int:order_id>', methods=['POST'])
@login_required
def confirm_receipt(order_id):
    """
    确认订单收货
    """
    try:
        # 获取当前用户 ID
        user_id = session.get('user_id')
        customer_id = get_customer_id_by_user_id(user_id)
        
        if not customer_id:
            return jsonify({'success': False, 'error': '无效的用户身份'}), 403
        
        # 更新订单状态为已完成
        db, cursor = get_db()
        cursor.execute("""
            UPDATE orders
            SET order_status = 'completed'
            WHERE order_id = %s AND customer_id = %s
        """, (order_id, customer_id))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'error': '订单不存在或无法更新'}), 404

        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        
        return jsonify({'success': False, 'error': '系统错误，无法确认收货'}), 500


@app.route('/submit_review', methods=['POST'])
@login_required
def submit_review():
    """
    接收前端傳來的訂單評分並存入資料庫
    """
    try:
        data = request.json  # 如果前端用的是 JSON 發送
        app.logger.info(f"接收到的評分數據: {data}")

        order_id = data.get('order_id')
        menu_id = data.get('menu_id')
        rating = data.get('rating')
        comments = data.get('comments')

        # 從 session 中獲取用戶 ID 並獲取客戶 ID
        user_id = session.get('user_id')
        customer_id = get_customer_id_by_user_id(user_id)

        if not all([order_id, rating, customer_id]):
            app.logger.error('缺少必要的資料')
            return jsonify({'success': False, 'error': '缺少必要的資料'}), 400

        # 插入評分到 reviews 表
        add_review(order_id, customer_id, menu_id, rating, comments)
        app.logger.info('評分成功插入資料庫')
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"提交評分時發生錯誤: {e}")
        return jsonify({'success': False, 'error': '系統錯誤，請稍後再試'}), 500


@app.route('/reviews/<int:restaurant_id>', methods=['GET'])
@login_required
def reviews(restaurant_id):
    """
    顯示指定商家的評論頁面
    """
    try:
        # 獲取該商家相關的評論
        reviews = get_reviews_by_restaurant(restaurant_id)

        # 獲取該商家資訊
        merchant = get_merchant_by_id(restaurant_id)

        return render_template('customer/reviews.html', reviews=reviews, merchant=merchant)
    except Exception as e:
        app.logger.error(f"Error fetching reviews for restaurant_id {restaurant_id}: {e}")
        return render_template('customer/reviews.html', reviews=[], merchant={})


    
if __name__ == '__main__':
    app.run(debug=True)
