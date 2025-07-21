from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import or_

app = Flask(__name__)

# SQLAlchemy Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dashadmin:123456789@localhost/customer_dashboard'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    plan = db.Column(db.String(50))
    expert = db.Column(db.String(50))
    signup_date = db.Column(db.Date)
    future_contact = db.Column(db.Date)
    payment_status = db.Column(db.String(20), default='unpaid')
    total_send = db.Column(db.Integer, default=0)
    onboarded = db.Column(db.Boolean, default=False)
    reports = db.relationship('Report', backref='customer', lazy=True)

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    date = db.Column(db.Date, default=datetime.utcnow)
    expert = db.Column(db.String(50))
    report_type = db.Column(db.String(50))
    work_done = db.Column(db.String(100))
    goal = db.Column(db.String(100))
    description = db.Column(db.Text)
    future_contact_date = db.Column(db.Date)
    problem_type = db.Column(db.String(20), default='None')

# Create tables
with app.app_context():
    db.create_all()
# TypeError: '<' not supported between instances of 'datetime.date' and 'str'
# Routes
@app.route('/')
def dashboard():
    query = Customer.query
    
    # Apply filters
    if request.args.get('search'):
        search = request.args['search']
        query = query.filter(or_(
            Customer.full_name.ilike(f'%{search}%'),
            Customer.phone.ilike(f'%{search}%')
        ))
    
    if request.args.get('expert'):
        query = query.filter_by(expert=request.args['expert'])
    
    if request.args.get('start_date'):
        query = query.filter(Customer.signup_date >= request.args['start_date'])
    
    if request.args.get('end_date'):
        query = query.filter(Customer.signup_date <= request.args['end_date'])
    
    customers = query.all()
    experts = db.session.query(Customer.expert).distinct().all()
    
    # Calculate due contacts count
    today = datetime.now().date()
    due_contacts_count = Customer.query.filter(
        Customer.future_contact <= today
    ).count()
    
    return render_template('dashboard.html',
                        customers=customers,
                        experts=[e[0] for e in experts if e[0]],
                        request_args=request.args,
                        due_contacts_count=due_contacts_count)

@app.route('/customer/<int:customer_id>')
def customer_detail(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    reports = Report.query.filter_by(customer_id=customer_id).order_by(Report.date.desc()).all()
    return render_template('customer_detail.html',
                         customer=customer,
                         reports=reports)

@app.route('/customer/<int:customer_id>/add_report', methods=['POST'])
def add_report(customer_id):
    report = Report(
        customer_id=customer_id,
        # date=datetime.strptime(request.form['date'], '%Y-%m-%d') if request.form['date'] else datetime.utcnow(),
        expert=request.form['expert'],
        report_type=request.form['report_type'],
        work_done=request.form['work_done'],
        goal=request.form['goal'],
        description=request.form['description'],
        future_contact_date=datetime.strptime(request.form['future_contact'], '%Y-%m-%d'),
        problem_type=request.form.get('problem_type', 'None')
    )
    db.session.add(report)
    db.session.commit()
    return redirect(url_for('customer_detail', customer_id=customer_id))

@app.route('/due-contacts')
def due_contacts():
    today = datetime.now().date()
    customers = Customer.query.filter(
        Customer.future_contact <= today
    ).order_by(Customer.future_contact.asc()).all()
    return render_template('due_contacts.html',
                         customers=customers,
                         today=today.strftime('%Y-%m-%d'))

@app.route('/customer/<int:customer_id>/mark_contacted', methods=['POST'])
def mark_contacted(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    customer.future_contact = datetime.strptime(request.form['new_contact_date'], '%Y-%m-%d').date()
    db.session.commit()
    return redirect(url_for('customer_detail', customer_id=customer_id))

if __name__ == '__main__':
    app.run(debug=True)