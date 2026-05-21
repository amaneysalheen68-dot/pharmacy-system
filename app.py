from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Patient, Doctor, Pharmacist, Drug, Prescription, Sale, SaleDetails, seed_database, create_user
from datetime import datetime, date, timedelta
from sqlalchemy import func
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pharmacy-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pharmacy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables and seed data
with app.app_context():
    db.create_all()
    seed_database()

# ========== Login Decorators ==========
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Access denied! Admin only.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def pharmacist_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') not in ['admin', 'pharmacist']:
            flash('Access denied!', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ========== Auth Routes ==========
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['role'] = user.role
            session['full_name'] = user.full_name
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

# ========== Registration Route ==========
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        full_name = request.form['full_name']
        role = request.form['role']
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))
        
        success, message = create_user(username, password, role, full_name)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')

# ========== User Management (Admin only) ==========
@app.route('/users')
@admin_required
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@app.route('/delete_user/<int:user_id>')
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == session.get('username'):
        flash('You cannot delete your own account!', 'danger')
    elif user.username == 'admin' and User.query.count() == 1:
        flash('Cannot delete the only admin account!', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} deleted successfully!', 'success')
    
    return redirect(url_for('users'))

# ========== Helper Functions ==========
def get_dashboard_stats():
    total_patients = Patient.query.count()
    total_doctors = Doctor.query.count()
    total_drugs = Drug.query.count()
    total_sales = db.session.query(func.sum(Sale.total_amount)).scalar() or 0
    low_stock_count = Drug.query.filter(Drug.stock_qty < 20).count()
    monthly_sales = db.session.query(func.sum(Sale.total_amount)).filter(
        Sale.sale_date >= datetime.now().replace(day=1)
    ).scalar() or 0
    
    return {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_drugs': total_drugs,
        'total_sales': total_sales,
        'low_stock_count': low_stock_count,
        'monthly_sales': monthly_sales
    }

# ========== Main Routes ==========
@app.route('/')
@login_required
def index():
    stats = get_dashboard_stats()
    recent_sales = Sale.query.order_by(Sale.sale_date.desc()).limit(5).all()
    low_stock = Drug.query.filter(Drug.stock_qty < 20).limit(5).all()
    return render_template('index.html', stats=stats, recent_sales=recent_sales, low_stock=low_stock)

# ========== Patients (Admin only can add/delete) ==========
@app.route('/patients')
@login_required
def patients():
    all_patients = Patient.query.all()
    return render_template('patients.html', patients=all_patients)

@app.route('/add_patient', methods=['POST'])
@admin_required
def add_patient():
    patient = Patient(
        name=request.form['name'],
        phone=request.form['phone'],
        address=request.form['address'],
        birth_date=datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date() if request.form['birth_date'] else None
    )
    db.session.add(patient)
    db.session.commit()
    flash('✅ Patient added successfully!', 'success')
    return redirect(url_for('patients'))

@app.route('/delete_patient/<int:patient_id>')
@admin_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    flash('🗑️ Patient deleted!', 'success')
    return redirect(url_for('patients'))

# ========== Doctors (Admin only can add/delete) ==========
@app.route('/doctors')
@login_required
def doctors():
    all_doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=all_doctors)

@app.route('/add_doctor', methods=['POST'])
@admin_required
def add_doctor():
    doctor = Doctor(
        name=request.form['name'],
        specialisation=request.form['specialisation'],
        phone=request.form['phone'],
        license_no=request.form['license_no']
    )
    db.session.add(doctor)
    db.session.commit()
    flash('✅ Doctor added successfully!', 'success')
    return redirect(url_for('doctors'))

@app.route('/delete_doctor/<int:doctor_id>')
@admin_required
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    db.session.delete(doctor)
    db.session.commit()
    flash('🗑️ Doctor deleted!', 'success')
    return redirect(url_for('doctors'))

# ========== Pharmacists (Admin only) ==========
@app.route('/pharmacists')
@admin_required
def pharmacists():
    all_pharmacists = Pharmacist.query.all()
    return render_template('pharmacists.html', pharmacists=all_pharmacists)

@app.route('/add_pharmacist', methods=['POST'])
@admin_required
def add_pharmacist():
    pharmacist = Pharmacist(
        name=request.form['name'],
        phone=request.form['phone'],
        shift=request.form['shift'],
        license_no=request.form['license_no']
    )
    db.session.add(pharmacist)
    db.session.commit()
    flash('✅ Pharmacist added successfully!', 'success')
    return redirect(url_for('pharmacists'))

@app.route('/delete_pharmacist/<int:pharmacist_id>')
@admin_required
def delete_pharmacist(pharmacist_id):
    pharmacist = Pharmacist.query.get_or_404(pharmacist_id)
    db.session.delete(pharmacist)
    db.session.commit()
    flash('🗑️ Pharmacist deleted!', 'success')
    return redirect(url_for('pharmacists'))

# ========== Drugs ==========
@app.route('/drugs')
@login_required
def drugs():
    all_drugs = Drug.query.all()
    category = request.args.get('category')
    if category:
        all_drugs = Drug.query.filter_by(category=category).all()
    categories = db.session.query(Drug.category).distinct().all()
    return render_template('drugs.html', drugs=all_drugs, categories=[c[0] for c in categories if c[0]])

@app.route('/add_drug', methods=['POST'])
@admin_required
def add_drug():
    drug = Drug(
        name=request.form['name'],
        category=request.form['category'],
        price=float(request.form['price']),
        stock_qty=int(request.form['stock_qty']),
        expiry_date=datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date() if request.form['expiry_date'] else None,
        manufacturer=request.form['manufacturer']
    )
    db.session.add(drug)
    db.session.commit()
    flash('✅ Drug added successfully!', 'success')
    return redirect(url_for('drugs'))

@app.route('/update_drug/<int:drug_id>', methods=['POST'])
@admin_required
def update_drug(drug_id):
    drug = Drug.query.get_or_404(drug_id)
    drug.name = request.form['name']
    drug.category = request.form['category']
    drug.price = float(request.form['price'])
    drug.stock_qty = int(request.form['stock_qty'])
    drug.manufacturer = request.form['manufacturer']
    if request.form['expiry_date']:
        drug.expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date()
    db.session.commit()
    flash('✅ Drug updated successfully!', 'success')
    return redirect(url_for('drugs'))

@app.route('/delete_drug/<int:drug_id>')
@admin_required
def delete_drug(drug_id):
    drug = Drug.query.get_or_404(drug_id)
    db.session.delete(drug)
    db.session.commit()
    flash('🗑️ Drug deleted!', 'success')
    return redirect(url_for('drugs'))

@app.route('/update_stock/<int:drug_id>', methods=['POST'])
@pharmacist_required
def update_stock(drug_id):
    drug = Drug.query.get_or_404(drug_id)
    drug.stock_qty = int(request.form['stock_qty'])
    db.session.commit()
    flash('✅ Stock updated!', 'success')
    return redirect(url_for('drugs'))

# ========== Prescriptions ==========
@app.route('/prescriptions')
@login_required
def prescriptions():
    all_prescriptions = Prescription.query.all()
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    return render_template('prescription.html', prescriptions=all_prescriptions, patients=patients, doctors=doctors)

@app.route('/add_prescription', methods=['POST'])
@pharmacist_required
def add_prescription():
    prescription = Prescription(
        patient_id=int(request.form['patient_id']),
        doctor_id=int(request.form['doctor_id']),
        issue_date=datetime.strptime(request.form['issue_date'], '%Y-%m-%d').date(),
        notes=request.form['notes']
    )
    db.session.add(prescription)
    db.session.commit()
    flash('✅ Prescription created!', 'success')
    return redirect(url_for('prescriptions'))

# ========== Sales ==========
@app.route('/sales')
@pharmacist_required
def sales():
    all_sales = Sale.query.all()
    patients = Patient.query.all()
    pharmacists = Pharmacist.query.all()
    prescriptions = Prescription.query.all()
    drugs = Drug.query.all()
    return render_template('sale.html', sales=all_sales, patients=patients, pharmacists=pharmacists, prescriptions=prescriptions, drugs=drugs)

@app.route('/add_sale', methods=['POST'])
@pharmacist_required
def add_sale():
    patient_id = int(request.form['patient_id'])
    pharmacist_obj = Pharmacist.query.first()
    pharmacist_id = pharmacist_obj.pharmacist_id if pharmacist_obj else 1
    prescription_id = int(request.form['prescription_id']) if request.form.get('prescription_id') else None
    
    sale = Sale(
        patient_id=patient_id,
        pharmacist_id=pharmacist_id,
        prescription_id=prescription_id,
        total_amount=0
    )
    db.session.add(sale)
    db.session.flush()
    
    drug_ids = request.form.getlist('drug_id[]')
    quantities = request.form.getlist('quantity[]')
    total = 0
    
    for drug_id, qty in zip(drug_ids, quantities):
        if drug_id and qty and int(qty) > 0:
            drug = Drug.query.get(int(drug_id))
            if drug and drug.stock_qty >= int(qty):
                subtotal = drug.price * int(qty)
                total += subtotal
                detail = SaleDetails(
                    sale_id=sale.sale_id,
                    drug_id=int(drug_id),
                    quantity=int(qty),
                    subtotal=subtotal
                )
                db.session.add(detail)
                drug.stock_qty -= int(qty)
            else:
                flash(f'❌ Insufficient stock for {drug.name}', 'danger')
                db.session.rollback()
                return redirect(url_for('sales'))
    
    sale.total_amount = total
    db.session.commit()
    flash(f'💰 Sale completed! Total: ${total:.2f}', 'success')
    return redirect(url_for('sales'))

# ========== Reports (Admin only) ==========
@app.route('/reports')
@admin_required
def reports():
    sales_data = Sale.query.all()
    drugs_data = Drug.query.all()
    total_sales = sum(s.total_amount for s in sales_data)
    total_transactions = len(sales_data)
    low_stock = Drug.query.filter(Drug.stock_qty < 20).all()
    
    last_7_days = []
    for i in range(6, -1, -1):
        day = datetime.now().date() - timedelta(days=i)
        day_sales = db.session.query(func.sum(Sale.total_amount)).filter(
            func.date(Sale.sale_date) == day
        ).scalar() or 0
        last_7_days.append({'date': day.strftime('%a'), 'amount': day_sales})
    
    return render_template('reports.html', 
                         sales_data=sales_data,
                         drugs_data=drugs_data,
                         total_sales=total_sales,
                         total_transactions=total_transactions,
                         low_stock=low_stock,
                         chart_data=last_7_days)

# ========== API ==========
@app.route('/api/sales_summary')
@login_required
def api_sales_summary():
    sales = Sale.query.all()
    return jsonify({
        'total_sales': sum(s.total_amount for s in sales),
        'total_transactions': len(sales),
        'date': str(date.today())
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)