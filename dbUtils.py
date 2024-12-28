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

def get_merchants_revenue(): #列出各商家應收金額
    db, cursor = get_db()
    cursor.execute("""
        SELECT rd.restaurant_name, SUM(o.total_amount) AS total_revenue
        FROM orders o
        JOIN restaurant_details rd ON o.restaurant_id = rd.restaurant_id
        GROUP BY o.restaurant_id;
    """)
    result = cursor.fetchall()
    return result

def get_delivery_person_orders(): #列出各小哥接單數
    db, cursor = get_db()
    cursor.execute("""
        SELECT dpd.full_name, COUNT(o.order_id) AS total_orders
        FROM orders o
        JOIN delivery_person_details dpd ON o.delivery_person_id = dpd.delivery_id
        GROUP BY o.delivery_person_id;
    """)
    result = cursor.fetchall()
    return result

def get_customers_due_amount(): #列出各客戶應付金額
    db, cursor = get_db()
    cursor.execute("""
        SELECT cd.full_name, SUM(o.total_amount) AS due_amount
        FROM orders o
        JOIN customer_details cd ON o.customer_id = cd.customer_id
        GROUP BY o.customer_id;
    """)
    result = cursor.fetchall()
    return result
