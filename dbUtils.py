import mysql.connector
from flask import current_app, g

def connect_db():
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=current_app.config['MYSQL_HOST'],
                user=current_app.config['MYSQL_USER'],
                password=current_app.config['MYSQL_PASSWORD'],
                database=current_app.config['MYSQL_DB'],
                port=current_app.config['MYSQL_PORT']
            )
            g.cursor = g.db.cursor(dictionary=True)
            current_app.logger.debug('Database connection established')
        except mysql.connector.Error as e:
            current_app.logger.error(f"Error connecting to DB: {e}")
            exit(1)
    return g.db, g.cursor

def get_db():
    db, cursor = connect_db()
    return db, cursor

def close_db(e=None):
    db = g.pop('db', None)
    cursor = g.pop('cursor', None)
    if cursor is not None:
        cursor.close()
    if db is not None:
        db.close()


def validate_login(username, password):
    db, cursor = get_db()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    
    if user and user['password'] == password:
        return user
    return None

def get_role_table(role):
    role_tables = {
        1: 'restaurant_details',
        2: 'delivery_person_details',
        3: 'customer_details',
        4: 'platform_details'
    }
    return role_tables.get(role)

def get_user(user_id):
    db, cursor = get_db()
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    return user

def register_user(username, password, role):
    db, cursor = get_db()
    cursor.execute("INSERT INTO users (username, role, password) VALUES (%s, %s, %s)", 
                           (username, role, password))
    if role == 4:
            cursor.execute(
                "INSERT INTO platform_details (platform_id, password, platform_name) VALUES (%s, %s, %s)", 
                (cursor.lastrowid, password, username)
            )
    db.commit()

def get_merchants_revenue():
    db, cursor = get_db()
    cursor.execute("""
        SELECT rd.restaurant_name, SUM(o.total_amount) AS total_revenue
        FROM orders o
        JOIN restaurant_details rd ON o.restaurant_id = rd.restaurant_id
        GROUP BY o.restaurant_id;
    """)
    result = cursor.fetchall()
    return result

def get_delivery_person_orders():
    db, cursor = get_db()
    cursor.execute("""
        SELECT dpd.full_name, COUNT(o.order_id) AS total_orders
        FROM orders o
        JOIN delivery_person_details dpd ON o.delivery_person_id = dpd.delivery_id
        GROUP BY o.delivery_person_id;
    """)
    result = cursor.fetchall()
    return result

def get_customers_due_amount():
    db, cursor = get_db()
    cursor.execute("""
        SELECT cd.full_name, SUM(o.total_amount) AS due_amount
        FROM orders o
        JOIN customer_details cd ON o.customer_id = cd.customer_id
        GROUP BY o.customer_id;
    """)
    result = cursor.fetchall()
    return result
#餐廳
def add_menu_item(restaurant_id, item_name, price):
    """
    新增菜品到資料庫
    :param restaurant_id: 餐廳ID
    :param item_name: 菜品名稱
    :param price: 菜品價格
    :return: 插入成功回傳 True，失敗拋出異常
    """
    try:
        db, cursor = get_db()
        cursor.execute(
            "INSERT INTO menu (restaurant_id, item_name, price, availability) VALUES (%s, %s, %s, 1)",
            (restaurant_id, item_name, price)
        )
        db.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"Error adding menu item: {e}")
        db.rollback()
        raise e

def get_menu_item(restaurant_id):
    try:
        db, cursor = get_db()
        cursor.execute("SELECT item_name, price FROM menu WHERE restaurant_id = %s",(restaurant_id,))
        menu_items = cursor.fetchall()
        return menu_items
    except Exception as e:
        current_app.logger.error(f"Error fetching menu items: {e}")
        return []

#小哥
def get_pending_order():
        db, cursor = get_db()
        cursor.execute("SELECT * FROM orders WHERE order_status = 'pending'")
        pending_orders = cursor.fetchall()
        return pending_orders
def get_accepted_order():
        db, cursor = get_db()
        cursor.execute("SELECT * FROM orders WHERE order_status = 'confirmed'")
        accepted_orders = cursor.fetchall()
        return accepted_orders
def get_completed_order():
        db, cursor = get_db()
        cursor.execute("SELECT * FROM orders WHERE order_status = 'completed'")
        completed_orders = cursor.fetchall()
        return completed_orders

def get_order_detail(order_id):
        db, cursor = get_db()
        cursor.execute("""
            SELECT 
                o.order_id, 
                c.full_name AS customer_name, 
                r.restaurant_name, 
                o.total_amount, 
                o.order_status, 
                o.created_at, 
                d.full_name AS delivery_person_name
            FROM orders o
            LEFT JOIN customer_details c ON o.customer_id = c.customer_id
            LEFT JOIN restaurant_details r ON o.restaurant_id = r.restaurant_id
            LEFT JOIN delivery_person_details d ON o.delivery_person_id = d.delivery_id
            WHERE o.order_id = %s
        """, (order_id,))
        
        # 取得查詢結果
        order = cursor.fetchone()
        return order

#客戶
def get_all_restaurants():
    """
    從資料庫獲取所有餐廳的資訊
    """
    db, cursor = get_db()
    try:
        cursor.execute("SELECT * FROM restaurant_details")
        return cursor.fetchall()  # 返回所有商家資料
    except Exception as e:
        current_app.logger.error(f"Error fetching all restaurants: {e}")
        raise e


def get_menu(restaurant_id):
    """
    根據餐廳 ID 獲取菜單
    """
    db, cursor = get_db()
    try:
        cursor.execute("SELECT * FROM menu WHERE restaurant_id = %s", (restaurant_id,))
        return cursor.fetchall()  # 返回該餐廳的所有菜單項目
    except Exception as e:
        current_app.logger.error(f"Error fetching menu: {e}")
        raise e


	
def get_order_details(order_id):
    db, cursor = get_db()
    cursor.execute("""
        SELECT 
            o.order_id, 
            o.customer_id, 
            o.restaurant_id, 
            o.total_amount, 
            o.order_status, 
            d.menu_id, 
            m.item_name, 
            d.quantity, 
            m.price, 
            (d.quantity * m.price) AS item_total
        FROM orders o
        JOIN order_details d ON o.order_id = d.order_id
        JOIN menu m ON d.menu_id = m.menu_id
        WHERE o.order_id = %s
    """, (order_id,))
    return cursor.fetchall()


def get_order_status(order_id):
    db, cursor = get_db()
    cursor.execute("SELECT order_status FROM orders WHERE order_id = %s", (order_id,))
    return cursor.fetchone()

	
def update_order_status(order_id, status):
    db, cursor = get_db()
    cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s", (status, order_id))
    db.commit()


def submit_review(order_id, customer_id, menu_id, rating, comments):
    db, cursor = get_db()
    cursor.execute("""
        INSERT INTO reviews (order_id, customer_id, menu_id, rating, comments)
        VALUES (%s, %s, %s, %s, %s)
    """, (order_id, customer_id, menu_id, rating, comments))
    db.commit()

	
def get_reviews(menu_id):
    db, cursor = get_db()
    cursor.execute("""
        SELECT r.review_id, r.rating, r.comments, r.created_at, m.item_name
        FROM reviews r
        JOIN menu m ON r.menu_id = m.menu_id
        WHERE r.menu_id = %s
    """, (menu_id,))
    return cursor.fetchall()