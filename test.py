# from flask import Flask
# from flask_mysqldb import MySQL

# app = Flask(__name__)
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'dashadmin'
# app.config['MYSQL_PASSWORD'] = '123456789'
# app.config['MYSQL_DB'] = 'customer_dashboard'

# mysql = MySQL(app)

# @app.route('/test')
# def test():
#     try:
#         cur = mysql.connection.cursor()
#         cur.execute("SELECT 1")
#         result = cur.fetchone()
#         cur.close()
#         return f"Database connection OK! Result: {result}"
#     except Exception as e:
#         return f"Connection failed: {str(e)}"

# if __name__ == '__main__':
#     app.run(debug=True)

from app import app, mysql
from datetime import datetime, timedelta

with app.app_context():
    cur = mysql.connection.cursor()
    
    # Add sample customer
    cur.execute("""
    INSERT INTO customers 
    (full_name, phone, plan, expert, signup_date, future_contact, payment_status, total_send, onboarded)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        "John Doe", "09100040029", "Premium", "Alex",
        datetime.now().date(), datetime.now().date() + timedelta(days=7),
        "paid", 42, True
    ))
    
    mysql.connection.commit()
    cur.close()