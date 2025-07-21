from app import app, mysql
from datetime import datetime
def recreate_tables():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # Drop tables if they exist
        cur.execute("DROP TABLE IF EXISTS reports")
        cur.execute("DROP TABLE IF EXISTS customers")
        
        # Recreate with correct schema
        cur.execute("""
        CREATE TABLE customers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            phone VARCHAR(20) UNIQUE NOT NULL,
            plan VARCHAR(50),
            expert VARCHAR(50),
            signup_date DATE,
            future_contact DATE,
            payment_status VARCHAR(20) DEFAULT 'unpaid',
            total_send INT DEFAULT 0,
            onboarded BOOLEAN DEFAULT FALSE
        )
        """)
        
        cur.execute("""
        CREATE TABLE reports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT,
            date DATE,
            expert VARCHAR(50),
            report_type VARCHAR(50),
            work_done VARCHAR(100),
            goal VARCHAR(100),
            description TEXT,
            future_contact_date DATE,
            problem_type VARCHAR(20),
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
        """)
        
        mysql.connection.commit()
        cur.close()
        print("Successfully recreated tables with correct schema")

if __name__ == '__main__':
    recreate_tables()