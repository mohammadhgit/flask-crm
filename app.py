from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Generate sample customer data
def generate_sample_customers(num=50):
    customers = []
    first_names = ["John", "Jane", "Michael", "Emily", "David", "Sarah"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
    plans = ["Basic", "Standard", "Premium", "Enterprise"]
    experts = ["Alex", "Sam", "Taylor", "Jordan", "Casey"]
    payment_statuses = ["paid", "unpaid", "partial"]
    
    for i in range(1, num+1):
        full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        customer = {
            "id": i,
            "fullName": full_name,
            "phone": f"09{random.randint(100000000, 999999999)}",
            "plan": random.choice(plans),
            "expert": random.choice(experts),
            "date": datetime(2023, random.randint(1, 12), random.randint(1, 28)).strftime("%Y-%m-%d"),
            "futureContact": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
            "paids": random.choice(payment_statuses),
            "totalSend": random.randint(0, 100),
            # Include other fields you might need for the detail page
            "sendStatus": random.choice(["sent", "pending", "failed"]),
            "workDone": random.choice(["completed", "in progress", "not started"]),
            "goal": random.choice(["weight loss", "muscle gain", "maintenance"]),
            "details": f"Details for {full_name}",
            "hasSent": random.choice([True, False]),
            "allSend": random.choice([True, False])
        }
        customers.append(customer)
    
    return customers

# Our in-memory "database"
customers_data = generate_sample_customers()

@app.route('/')
def dashboard():
    search_query = request.args.get('search', '').lower()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    expert_filter = request.args.get('expert', '')  # New expert filter
    
    filtered_customers = customers_data
    
    # Apply search filter
    if search_query:
        filtered_customers = [
            c for c in filtered_customers 
            if (search_query in c['fullName'].lower() or 
                search_query in c['phone'].lower())
        ]
    
    # Apply date filter
    if start_date:
        filtered_customers = [c for c in filtered_customers if c['date'] >= start_date]
    if end_date:
        filtered_customers = [c for c in filtered_customers if c['date'] <= end_date]
    
    # Apply expert filter
    if expert_filter:
        filtered_customers = [c for c in filtered_customers if c['expert'] == expert_filter]
    
    # Calculate due contacts count
    today = datetime.now().strftime("%Y-%m-%d")
    due_contacts_count = len([
        c for c in customers_data 
        if c.get('futureContact') and c['futureContact'] <= today
    ])
    
    # Get unique experts for dropdown
    experts = sorted(list({c['expert'] for c in customers_data if c.get('expert')}))
    
        # Calculate due contacts count
    today = datetime.now().strftime("%Y-%m-%d")
    due_contacts_count = len([
        c for c in customers_data 
        if c.get('futureContact') and c['futureContact'] <= today
    ])
    
    return render_template('dashboard.html', 
                         customers=filtered_customers,
                         due_contacts_count=due_contacts_count,
                         experts=expert_filter,
                         all_experts=experts)
    # return render_template('dashboard.html', customers=filtered_customers)

@app.route('/customer/<int:customer_id>')
def customer_detail(customer_id):
    customer = next((c for c in customers_data if c['id'] == customer_id), None)
    if not customer:
        return "Customer not found", 404
    
    return render_template('customer_detail.html', customer=customer)
@app.route('/customer/<int:customer_id>/add_report', methods=['POST'])
def add_report(customer_id):
    customer = next((c for c in customers_data if c['id'] == customer_id), None)
    if not customer:
        return "Customer not found", 404
    
    new_report = {
        "id": len(customer.get('reports', [])) + 1,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "expert": request.form.get('expert'),
        "type": request.form.get('report_type'),
        "workDone": request.form.get('work_done'),
        "goal": request.form.get('goal'),
        "description": request.form.get('description'),
        "futureContact": request.form.get('future_contact')
    }
    
    if 'reports' not in customer:
        customer['reports'] = []
    customer['reports'].append(new_report)
    
    # Update the customer's expert if changed in the report
    customer['expert'] = new_report['expert']
    
    return redirect(url_for('customer_detail', customer_id=customer_id))
# customer['onboarded'] = customer['paids'] == 'paid' and customer['hasSent']


@app.route('/due-contacts')
def due_contacts():
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Get customers with futureContact <= today
    due_customers = [
        c for c in customers_data 
        if c.get('futureContact') and c['futureContact'] <= today
    ]
    
    return render_template('due_contacts.html', customers=due_customers, today=today)

@app.route('/customer/<int:customer_id>/mark-contacted', methods=['POST'])
def mark_contacted(customer_id):
    customer = next((c for c in customers_data if c['id'] == customer_id), None)
    if not customer:
        return "Customer not found", 404
    
    # Update future contact date based on form input
    new_contact_date = request.form.get('new_contact_date')
    if new_contact_date:
        customer['futureContact'] = new_contact_date
    
    return redirect(url_for('customer_detail', customer_id=customer_id))

if __name__ == '__main__':
    app.run(debug=True)