from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import random

db = SQLAlchemy()

# ========== جدول المستخدمين ==========
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Patient(db.Model):
    __tablename__ = 'patient'
    patient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    birth_date = db.Column(db.Date)
    
    prescriptions = db.relationship('Prescription', backref='patient', lazy=True)
    sales = db.relationship('Sale', backref='patient', lazy=True)

class Doctor(db.Model):
    __tablename__ = 'doctor'
    doctor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialisation = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    license_no = db.Column(db.String(50), unique=True)
    
    prescriptions = db.relationship('Prescription', backref='doctor', lazy=True)

class Pharmacist(db.Model):
    __tablename__ = 'pharmacist'
    pharmacist_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    shift = db.Column(db.String(20))
    license_no = db.Column(db.String(50), unique=True)
    
    sales = db.relationship('Sale', backref='pharmacist', lazy=True)

class Drug(db.Model):
    __tablename__ = 'drug'
    drug_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    price = db.Column(db.Float, nullable=False)
    stock_qty = db.Column(db.Integer, default=0)
    expiry_date = db.Column(db.Date)
    manufacturer = db.Column(db.String(100))
    
    sale_details = db.relationship('SaleDetails', backref='drug', lazy=True)

class Prescription(db.Model):
    __tablename__ = 'prescription'
    prescription_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'))
    issue_date = db.Column(db.Date, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    sales = db.relationship('Sale', backref='prescription', lazy=True)

class Sale(db.Model):
    __tablename__ = 'sale'
    sale_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'))
    pharmacist_id = db.Column(db.Integer, db.ForeignKey('pharmacist.pharmacist_id'))
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescription.prescription_id'))
    total_amount = db.Column(db.Float, default=0.0)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    details = db.relationship('SaleDetails', backref='sale', lazy=True)

class SaleDetails(db.Model):
    __tablename__ = 'sale_details'
    sale_item_id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.sale_id'))
    drug_id = db.Column(db.Integer, db.ForeignKey('drug.drug_id'))
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)


# ========== دالة لإنشاء مستخدم جديد ==========
def create_user(username, password, role, full_name):
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return False, "Username already exists!"
    
    if role not in ['admin', 'pharmacist']:
        return False, "Invalid role! Choose admin or pharmacist."
    
    if len(password) < 4:
        return False, "Password must be at least 4 characters!"
    
    new_user = User(
        username=username,
        full_name=full_name,
        role=role
    )
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return True, f"User {username} created successfully!"


# ========== دالة لإدخال بيانات تجريبية ==========
def seed_database():
    if User.query.first() is not None:
        print("✅ Database already has data, skipping seed...")
        return
    
    print("🌱 Seeding database with sample data...")
    
    # 0. Create Users
    users = [
        User(username="admin", full_name="System Administrator", role="admin"),
        User(username="pharmacist1", full_name="Ahmed Hassan", role="pharmacist"),
        User(username="pharmacist2", full_name="Sara Mahmoud", role="pharmacist"),
    ]
    for user in users:
        user.set_password("123456")
    db.session.add_all(users)
    
    # 1. Create Doctors (30 doctors)
    doctors = [
        # Cardiology (4)
        Doctor(name="Dr. Ahmed Mansour", specialisation="Cardiology", phone="01001234567", license_no="DOC001"),
        Doctor(name="Dr. Mahmoud Reda", specialisation="Cardiology", phone="01001234568", license_no="DOC002"),
        Doctor(name="Dr. Hany Zaki", specialisation="Cardiology", phone="01001234569", license_no="DOC003"),
        Doctor(name="Dr. Amr Khaled", specialisation="Cardiology", phone="01001234570", license_no="DOC004"),
        
        # Pediatrics (3)
        Doctor(name="Dr. Sara Khaled", specialisation="Pediatrics", phone="01002345678", license_no="DOC005"),
        Doctor(name="Dr. Mai Hassan", specialisation="Pediatrics", phone="01002345679", license_no="DOC006"),
        Doctor(name="Dr. Nour El-Din", specialisation="Pediatrics", phone="01002345680", license_no="DOC007"),
        
        # Dermatology (3)
        Doctor(name="Dr. Mohamed Ali", specialisation="Dermatology", phone="01003456789", license_no="DOC008"),
        Doctor(name="Dr. Yasmin Ibrahim", specialisation="Dermatology", phone="01003456790", license_no="DOC009"),
        Doctor(name="Dr. Karim Adel", specialisation="Dermatology", phone="01003456791", license_no="DOC010"),
        
        # Neurology (2)
        Doctor(name="Dr. Nour Hassan", specialisation="Neurology", phone="01004567890", license_no="DOC011"),
        Doctor(name="Dr. Tamer Samir", specialisation="Neurology", phone="01004567891", license_no="DOC012"),
        
        # Orthopedics (3)
        Doctor(name="Dr. Youssef Kamel", specialisation="Orthopedics", phone="01005678901", license_no="DOC013"),
        Doctor(name="Dr. Sherif Lotfy", specialisation="Orthopedics", phone="01005678902", license_no="DOC014"),
        Doctor(name="Dr. Omar Farid", specialisation="Orthopedics", phone="01005678903", license_no="DOC015"),
        
        # Gynecology (3)
        Doctor(name="Dr. Amira Reda", specialisation="Gynecology", phone="01006789012", license_no="DOC016"),
        Doctor(name="Dr. Hala Mahmoud", specialisation="Gynecology", phone="01006789013", license_no="DOC017"),
        Doctor(name="Dr. Mona Samir", specialisation="Gynecology", phone="01006789014", license_no="DOC018"),
        
        # Psychiatry (2)
        Doctor(name="Dr. Khaled Ibrahim", specialisation="Psychiatry", phone="01007890123", license_no="DOC019"),
        Doctor(name="Dr. Rania Adel", specialisation="Psychiatry", phone="01007890124", license_no="DOC020"),
        
        # Ophthalmology (2)
        Doctor(name="Dr. Mona Lotfy", specialisation="Ophthalmology", phone="01008901234", license_no="DOC021"),
        Doctor(name="Dr. Ahmed Samy", specialisation="Ophthalmology", phone="01008901235", license_no="DOC022"),
        
        # ENT (2)
        Doctor(name="Dr. Hisham Fathy", specialisation="ENT", phone="01009012345", license_no="DOC023"),
        Doctor(name="Dr. Nabil Gamil", specialisation="ENT", phone="01009012346", license_no="DOC024"),
        
        # Urology (2)
        Doctor(name="Dr. Sameh Youssef", specialisation="Urology", phone="01000123456", license_no="DOC025"),
        Doctor(name="Dr. Ahmed Magdy", specialisation="Urology", phone="01000123457", license_no="DOC026"),
        
        # Internal Medicine (2)
        Doctor(name="Dr. Magdy Ezzat", specialisation="Internal Medicine", phone="01001234571", license_no="DOC027"),
        Doctor(name="Dr. Ashraf Sobhy", specialisation="Internal Medicine", phone="01001234572", license_no="DOC028"),
        
        # Endocrinology (1)
        Doctor(name="Dr. Eman Mostafa", specialisation="Endocrinology", phone="01002345681", license_no="DOC029"),
        
        # Rheumatology (1)
        Doctor(name="Dr. Waleed Hassan", specialisation="Rheumatology", phone="01003456792", license_no="DOC030"),
    ]
    db.session.add_all(doctors)
    
    # 2. Create Pharmacists
    pharmacists = [
        Pharmacist(name="Omar Samir", phone="01005678901", shift="Morning", license_no="PH001"),
        Pharmacist(name="Laila Mahmoud", phone="01006789012", shift="Evening", license_no="PH002"),
        Pharmacist(name="Youssef Ahmed", phone="01007890123", shift="Night", license_no="PH003"),
        Pharmacist(name="Nadia Ali", phone="01008901234", shift="Morning", license_no="PH004"),
    ]
    db.session.add_all(pharmacists)
    
    # 3. Create Patients
    patients = [
        Patient(name="Mariam Tarek", phone="01008901234", address="15 Ahmed Street, Cairo", birth_date=date(1990, 5, 10)),
        Patient(name="Khaled Ibrahim", phone="01009012345", address="22 Nile Road, Giza", birth_date=date(1985, 8, 22)),
        Patient(name="Fatima Adel", phone="01000123456", address="7 Palm Street, Alexandria", birth_date=date(2000, 3, 15)),
        Patient(name="Yassin Mostafa", phone="01001234568", address="44 New Cairo, Cairo", birth_date=date(1995, 11, 30)),
        Patient(name="Salma Hany", phone="01002345679", address="10 Maadi, Cairo", birth_date=date(1988, 7, 19)),
        Patient(name="Omar Hesham", phone="01003456780", address="5 Dokki, Giza", birth_date=date(1992, 2, 25)),
        Patient(name="Nour El-Din", phone="01004567891", address="12 Heliopolis, Cairo", birth_date=date(1998, 9, 8)),
        Patient(name="Hana Youssef", phone="01005678902", address="8 Zamalek, Cairo", birth_date=date(1993, 4, 12)),
        Patient(name="Seif Eldin", phone="01006789013", address="33 Nasr City, Cairo", birth_date=date(2001, 6, 20)),
        Patient(name="Laila Ahmed", phone="01007890124", address="19 Mohandiseen, Giza", birth_date=date(1987, 11, 5)),
    ]
    db.session.add_all(patients)
    db.session.flush()
    
    # 4. Create Drugs (100 drugs - same as before)
    drugs = [
        # Pain Relief (10)
        Drug(name="Paracetamol 500mg", category="Pain Relief", price=5.50, stock_qty=150, expiry_date=date(2025, 12, 31), manufacturer="Egypt Pharma"),
        Drug(name="Paracetamol 650mg", category="Pain Relief", price=7.00, stock_qty=120, expiry_date=date(2026, 1, 15), manufacturer="Egypt Pharma"),
        Drug(name="Ibuprofen 200mg", category="Pain Relief", price=8.00, stock_qty=200, expiry_date=date(2026, 1, 20), manufacturer="Delta Pharma"),
        Drug(name="Ibuprofen 400mg", category="Pain Relief", price=12.00, stock_qty=100, expiry_date=date(2026, 2, 10), manufacturer="Delta Pharma"),
        Drug(name="Aspirin 100mg", category="Pain Relief", price=4.50, stock_qty=300, expiry_date=date(2026, 3, 5), manufacturer="Alex Pharma"),
        Drug(name="Aspirin 300mg", category="Pain Relief", price=6.00, stock_qty=180, expiry_date=date(2026, 3, 20), manufacturer="Alex Pharma"),
        Drug(name="Diclofenac 50mg", category="Pain Relief", price=12.00, stock_qty=90, expiry_date=date(2025, 10, 15), manufacturer="EIPICO"),
        Drug(name="Diclofenac 100mg", category="Pain Relief", price=18.00, stock_qty=60, expiry_date=date(2025, 11, 1), manufacturer="EIPICO"),
        Drug(name="Naproxen 250mg", category="Pain Relief", price=15.00, stock_qty=60, expiry_date=date(2025, 9, 30), manufacturer="Pharco"),
        Drug(name="Naproxen 500mg", category="Pain Relief", price=22.00, stock_qty=40, expiry_date=date(2025, 10, 15), manufacturer="Pharco"),
        
        # Antibiotics (12)
        Drug(name="Amoxicillin 250mg", category="Antibiotics", price=12.00, stock_qty=80, expiry_date=date(2025, 8, 15), manufacturer="SEDICO"),
        Drug(name="Amoxicillin 500mg", category="Antibiotics", price=18.00, stock_qty=70, expiry_date=date(2025, 9, 10), manufacturer="SEDICO"),
        Drug(name="Amoxicillin Clavulanate 625mg", category="Antibiotics", price=28.00, stock_qty=50, expiry_date=date(2026, 1, 20), manufacturer="SEDICO"),
        Drug(name="Azithromycin 250mg", category="Antibiotics", price=18.00, stock_qty=55, expiry_date=date(2025, 7, 20), manufacturer="Hikma"),
        Drug(name="Azithromycin 500mg", category="Antibiotics", price=25.00, stock_qty=45, expiry_date=date(2025, 7, 20), manufacturer="Hikma"),
        Drug(name="Ciprofloxacin 250mg", category="Antibiotics", price=14.00, stock_qty=65, expiry_date=date(2025, 11, 10), manufacturer="EIPICO"),
        Drug(name="Ciprofloxacin 500mg", category="Antibiotics", price=18.00, stock_qty=55, expiry_date=date(2025, 11, 10), manufacturer="EIPICO"),
        Drug(name="Doxycycline 100mg", category="Antibiotics", price=20.00, stock_qty=40, expiry_date=date(2025, 12, 5), manufacturer="Pharco"),
        Drug(name="Clarithromycin 250mg", category="Antibiotics", price=22.00, stock_qty=35, expiry_date=date(2026, 2, 14), manufacturer="Hikma"),
        Drug(name="Levofloxacin 500mg", category="Antibiotics", price=30.00, stock_qty=30, expiry_date=date(2025, 9, 15), manufacturer="EIPICO"),
        Drug(name="Cefalexin 500mg", category="Antibiotics", price=15.00, stock_qty=60, expiry_date=date(2026, 1, 8), manufacturer="Delta Pharma"),
        Drug(name="Metronidazole 250mg", category="Antibiotics", price=8.00, stock_qty=100, expiry_date=date(2026, 3, 25), manufacturer="Alex Pharma"),
        
        # Digestive (12)
        Drug(name="Omeprazole 20mg", category="Digestive", price=15.00, stock_qty=45, expiry_date=date(2025, 10, 10), manufacturer="Delta Pharma"),
        Drug(name="Omeprazole 40mg", category="Digestive", price=22.00, stock_qty=35, expiry_date=date(2025, 11, 15), manufacturer="Delta Pharma"),
        Drug(name="Antinal 400mg", category="Digestive", price=10.00, stock_qty=120, expiry_date=date(2025, 9, 25), manufacturer="CID"),
        Drug(name="Mebeverine 135mg", category="Digestive", price=22.00, stock_qty=35, expiry_date=date(2026, 2, 14), manufacturer="EIPICO"),
        Drug(name="Domperidone 10mg", category="Digestive", price=8.50, stock_qty=70, expiry_date=date(2025, 8, 30), manufacturer="Alex Pharma"),
        Drug(name="Ranitidine 150mg", category="Digestive", price=12.00, stock_qty=90, expiry_date=date(2026, 1, 12), manufacturer="SEDICO"),
        Drug(name="Esomeprazole 20mg", category="Digestive", price=28.00, stock_qty=25, expiry_date=date(2025, 12, 20), manufacturer="Pharco"),
        Drug(name="Lansoprazole 30mg", category="Digestive", price=25.00, stock_qty=30, expiry_date=date(2026, 2, 28), manufacturer="EIPICO"),
        Drug(name="Metoclopramide 10mg", category="Digestive", price=6.00, stock_qty=110, expiry_date=date(2026, 3, 10), manufacturer="CID"),
        Drug(name="Buscopan 10mg", category="Digestive", price=14.00, stock_qty=85, expiry_date=date(2025, 9, 5), manufacturer="Delta Pharma"),
        Drug(name="Enterogermina", category="Digestive", price=18.00, stock_qty=60, expiry_date=date(2026, 5, 15), manufacturer="Sanofi"),
        Drug(name="Lactobacillus Probiotic", category="Digestive", price=25.00, stock_qty=45, expiry_date=date(2026, 4, 20), manufacturer="CID"),
        
        # Vitamins (12)
        Drug(name="Vitamin C 1000mg", category="Vitamins", price=18.00, stock_qty=60, expiry_date=date(2025, 9, 25), manufacturer="Pharco"),
        Drug(name="Vitamin C 500mg", category="Vitamins", price=12.00, stock_qty=85, expiry_date=date(2025, 10, 10), manufacturer="Pharco"),
        Drug(name="Vitamin D3 2000 IU", category="Vitamins", price=18.00, stock_qty=55, expiry_date=date(2026, 1, 15), manufacturer="SEDICO"),
        Drug(name="Vitamin D3 5000 IU", category="Vitamins", price=25.00, stock_qty=50, expiry_date=date(2026, 1, 15), manufacturer="SEDICO"),
        Drug(name="B-Complex", category="Vitamins", price=20.00, stock_qty=75, expiry_date=date(2025, 11, 20), manufacturer="EIPICO"),
        Drug(name="Zinc 50mg", category="Vitamins", price=12.00, stock_qty=85, expiry_date=date(2026, 4, 10), manufacturer="Delta Pharma"),
        Drug(name="Calcium 600mg", category="Vitamins", price=22.00, stock_qty=40, expiry_date=date(2025, 12, 1), manufacturer="CID"),
        Drug(name="Magnesium 400mg", category="Vitamins", price=20.00, stock_qty=50, expiry_date=date(2026, 3, 15), manufacturer="Pharco"),
        Drug(name="Omega-3 1000mg", category="Vitamins", price=35.00, stock_qty=45, expiry_date=date(2026, 6, 30), manufacturer="Seven Seas"),
        Drug(name="Multivitamin Adult", category="Vitamins", price=28.00, stock_qty=65, expiry_date=date(2026, 2, 28), manufacturer="Centrum"),
        Drug(name="Iron 50mg", category="Vitamins", price=14.00, stock_qty=70, expiry_date=date(2025, 11, 15), manufacturer="EIPICO"),
        Drug(name="Vitamin E 400 IU", category="Vitamins", price=16.00, stock_qty=55, expiry_date=date(2026, 5, 20), manufacturer="SEDICO"),
        
        # Allergy (8)
        Drug(name="Cetirizine 10mg", category="Allergy", price=7.00, stock_qty=95, expiry_date=date(2025, 11, 14), manufacturer="Alex Pharma"),
        Drug(name="Loratadine 10mg", category="Allergy", price=9.00, stock_qty=110, expiry_date=date(2026, 2, 28), manufacturer="SEDICO"),
        Drug(name="Fexofenadine 120mg", category="Allergy", price=28.00, stock_qty=30, expiry_date=date(2025, 7, 15), manufacturer="Hikma"),
        Drug(name="Desloratadine 5mg", category="Allergy", price=15.00, stock_qty=45, expiry_date=date(2026, 1, 10), manufacturer="Delta Pharma"),
        Drug(name="Bilastine 20mg", category="Allergy", price=22.00, stock_qty=35, expiry_date=date(2025, 12, 5), manufacturer="Pharco"),
        Drug(name="Hydroxyzine 25mg", category="Allergy", price=10.00, stock_qty=60, expiry_date=date(2026, 3, 18), manufacturer="CID"),
        Drug(name="Chlorpheniramine 4mg", category="Allergy", price=5.00, stock_qty=120, expiry_date=date(2026, 4, 25), manufacturer="Alex Pharma"),
        Drug(name="Levocetirizine 5mg", category="Allergy", price=12.00, stock_qty=70, expiry_date=date(2025, 10, 30), manufacturer="EIPICO"),
        
        # Blood Pressure & Diabetes (10)
        Drug(name="Metformin 500mg", category="Diabetes", price=22.00, stock_qty=30, expiry_date=date(2025, 7, 30), manufacturer="EIPICO"),
        Drug(name="Metformin 1000mg", category="Diabetes", price=30.00, stock_qty=25, expiry_date=date(2025, 8, 15), manufacturer="EIPICO"),
        Drug(name="Amlodipine 5mg", category="Blood Pressure", price=18.00, stock_qty=45, expiry_date=date(2026, 1, 25), manufacturer="Pharco"),
        Drug(name="Amlodipine 10mg", category="Blood Pressure", price=25.00, stock_qty=35, expiry_date=date(2026, 2, 10), manufacturer="Pharco"),
        Drug(name="Lisinopril 10mg", category="Blood Pressure", price=20.00, stock_qty=35, expiry_date=date(2025, 10, 18), manufacturer="SEDICO"),
        Drug(name="Lisinopril 20mg", category="Blood Pressure", price=28.00, stock_qty=25, expiry_date=date(2025, 11, 5), manufacturer="SEDICO"),
        Drug(name="Losartan 50mg", category="Blood Pressure", price=22.00, stock_qty=40, expiry_date=date(2026, 3, 12), manufacturer="Delta Pharma"),
        Drug(name="Valsartan 80mg", category="Blood Pressure", price=30.00, stock_qty=30, expiry_date=date(2025, 12, 20), manufacturer="Hikma"),
        Drug(name="Carvedilol 25mg", category="Blood Pressure", price=35.00, stock_qty=20, expiry_date=date(2026, 1, 28), manufacturer="EIPICO"),
        Drug(name="Bisoprolol 5mg", category="Blood Pressure", price=25.00, stock_qty=30, expiry_date=date(2026, 2, 15), manufacturer="Pharco"),
        
        # Cough & Cold (8)
        Drug(name="Cough Syrup Simple", category="Cough & Cold", price=15.00, stock_qty=65, expiry_date=date(2026, 3, 10), manufacturer="CID"),
        Drug(name="Pseudoephedrine 60mg", category="Cough & Cold", price=14.00, stock_qty=50, expiry_date=date(2025, 8, 5), manufacturer="Alex Pharma"),
        Drug(name="Dextromethorphan 15mg", category="Cough & Cold", price=16.00, stock_qty=55, expiry_date=date(2026, 1, 20), manufacturer="Delta Pharma"),
        Drug(name="Guaifenesin 200mg", category="Cough & Cold", price=12.00, stock_qty=70, expiry_date=date(2026, 4, 15), manufacturer="SEDICO"),
        Drug(name="Cold & Flu Capsules", category="Cough & Cold", price=18.00, stock_qty=80, expiry_date=date(2025, 11, 30), manufacturer="EIPICO"),
        Drug(name="Cough Lozenges", category="Cough & Cold", price=8.00, stock_qty=150, expiry_date=date(2026, 6, 1), manufacturer="CID"),
        Drug(name="Nose Spray Saline", category="Cough & Cold", price=12.00, stock_qty=60, expiry_date=date(2026, 5, 10), manufacturer="Alex Pharma"),
        Drug(name="Decongestant Tablets", category="Cough & Cold", price=15.00, stock_qty=45, expiry_date=date(2025, 12, 15), manufacturer="Pharco"),
        
        # Skincare (10)
        Drug(name="Clotrimazole Cream 1%", category="Skincare", price=12.00, stock_qty=80, expiry_date=date(2026, 5, 20), manufacturer="Delta Pharma"),
        Drug(name="Hydrocortisone Cream 1%", category="Skincare", price=18.00, stock_qty=45, expiry_date=date(2025, 12, 12), manufacturer="Pharco"),
        Drug(name="Tretinoin Cream 0.05%", category="Skincare", price=35.00, stock_qty=25, expiry_date=date(2025, 11, 1), manufacturer="EIPICO"),
        Drug(name="Benzoyl Peroxide 5%", category="Skincare", price=20.00, stock_qty=40, expiry_date=date(2026, 2, 28), manufacturer="CID"),
        Drug(name="Azelaic Acid 20%", category="Skincare", price=40.00, stock_qty=20, expiry_date=date(2026, 1, 15), manufacturer="SEDICO"),
        Drug(name="Moisturizing Cream", category="Skincare", price=15.00, stock_qty=100, expiry_date=date(2026, 7, 1), manufacturer="Nivea"),
        Drug(name="Sunscreen SPF 50", category="Skincare", price=25.00, stock_qty=60, expiry_date=date(2026, 8, 15), manufacturer="La Roche"),
        Drug(name="Salicylic Acid 2%", category="Skincare", price=22.00, stock_qty=35, expiry_date=date(2026, 3, 20), manufacturer="Delta Pharma"),
        Drug(name="Antifungal Powder", category="Skincare", price=10.00, stock_qty=70, expiry_date=date(2026, 4, 5), manufacturer="Alex Pharma"),
        Drug(name="Antibiotic Ointment", category="Skincare", price=14.00, stock_qty=85, expiry_date=date(2026, 6, 10), manufacturer="EIPICO"),
        
        # Respiratory (6)
        Drug(name="Salbutamol Inhaler", category="Respiratory", price=30.00, stock_qty=35, expiry_date=date(2026, 2, 10), manufacturer="Glaxo"),
        Drug(name="Budesonide Inhaler", category="Respiratory", price=45.00, stock_qty=20, expiry_date=date(2025, 12, 5), manufacturer="AstraZeneca"),
        Drug(name="Montelukast 10mg", category="Respiratory", price=25.00, stock_qty=30, expiry_date=date(2026, 1, 18), manufacturer="Hikma"),
        Drug(name="Theophylline 200mg", category="Respiratory", price=18.00, stock_qty=25, expiry_date=date(2025, 10, 25), manufacturer="Pharco"),
        Drug(name="Acetylcysteine 600mg", category="Respiratory", price=22.00, stock_qty=40, expiry_date=date(2026, 3, 30), manufacturer="SEDICO"),
        Drug(name="Fluticasone Nasal Spray", category="Respiratory", price=35.00, stock_qty=25, expiry_date=date(2026, 4, 20), manufacturer="GSK"),
        
        # Eye & Ear (6)
        Drug(name="Eye Drops Antibiotic", category="Eye & Ear", price=18.00, stock_qty=50, expiry_date=date(2026, 1, 10), manufacturer="Alcon"),
        Drug(name="Artificial Tears", category="Eye & Ear", price=15.00, stock_qty=70, expiry_date=date(2026, 5, 15), manufacturer="Bausch"),
        Drug(name="Ear Drops Antibiotic", category="Eye & Ear", price=16.00, stock_qty=45, expiry_date=date(2026, 2, 28), manufacturer="CID"),
        Drug(name="Anti-allergy Eye Drops", category="Eye & Ear", price=20.00, stock_qty=40, expiry_date=date(2025, 11, 20), manufacturer="Alcon"),
        Drug(name="Contact Lens Solution", category="Eye & Ear", price=25.00, stock_qty=60, expiry_date=date(2026, 7, 1), manufacturer="Bausch"),
        Drug(name="Eye Ointment", category="Eye & Ear", price=12.00, stock_qty=35, expiry_date=date(2026, 3, 10), manufacturer="EIPICO"),
        
        # Hormones (6)
        Drug(name="Thyroxine 50mcg", category="Hormones", price=15.00, stock_qty=40, expiry_date=date(2026, 2, 14), manufacturer="EIPICO"),
        Drug(name="Thyroxine 100mcg", category="Hormones", price=20.00, stock_qty=35, expiry_date=date(2026, 2, 28), manufacturer="EIPICO"),
        Drug(name="Prednisolone 5mg", category="Hormones", price=12.00, stock_qty=50, expiry_date=date(2025, 9, 30), manufacturer="Pharco"),
        Drug(name="Dexamethasone 0.5mg", category="Hormones", price=10.00, stock_qty=60, expiry_date=date(2026, 1, 20), manufacturer="SEDICO"),
        Drug(name="Insulin Injection", category="Hormones", price=120.00, stock_qty=20, expiry_date=date(2025, 12, 15), manufacturer="Novo Nordisk"),
        Drug(name="Oral Contraceptive Pills", category="Hormones", price=25.00, stock_qty=55, expiry_date=date(2026, 4, 30), manufacturer="Bayer"),
        
        # Nervous System (6)
        Drug(name="Diazepam 5mg", category="Nervous System", price=8.00, stock_qty=60, expiry_date=date(2026, 1, 15), manufacturer="Roche"),
        Drug(name="Amitriptyline 25mg", category="Nervous System", price=10.00, stock_qty=45, expiry_date=date(2025, 11, 10), manufacturer="Pharco"),
        Drug(name="Fluoxetine 20mg", category="Nervous System", price=18.00, stock_qty=40, expiry_date=date(2026, 2, 20), manufacturer="Eli Lilly"),
        Drug(name="Sertraline 50mg", category="Nervous System", price=22.00, stock_qty=35, expiry_date=date(2026, 3, 5), manufacturer="Pfizer"),
        Drug(name="Pregabalin 75mg", category="Nervous System", price=35.00, stock_qty=25, expiry_date=date(2025, 10, 28), manufacturer="Hikma"),
        Drug(name="Gabapentin 300mg", category="Nervous System", price=28.00, stock_qty=30, expiry_date=date(2026, 1, 12), manufacturer="Delta Pharma"),
    ]
    db.session.add_all(drugs)
    db.session.flush()
    
    # 5. Create Prescriptions (20 prescriptions)
    prescriptions = [
        Prescription(patient_id=patients[0].patient_id, doctor_id=doctors[0].doctor_id, issue_date=date(2025, 5, 1), notes="Take twice daily after meals - High blood pressure"),
        Prescription(patient_id=patients[1].patient_id, doctor_id=doctors[4].doctor_id, issue_date=date(2025, 5, 5), notes="For cough and fever - Pediatric dose"),
        Prescription(patient_id=patients[2].patient_id, doctor_id=doctors[7].doctor_id, issue_date=date(2025, 5, 10), notes="Apply cream twice daily for skin rash"),
        Prescription(patient_id=patients[3].patient_id, doctor_id=doctors[10].doctor_id, issue_date=date(2025, 5, 12), notes="Take before breakfast - Neurological evaluation"),
        Prescription(patient_id=patients[4].patient_id, doctor_id=doctors[0].doctor_id, issue_date=date(2025, 5, 15), notes="For blood pressure monitoring"),
        Prescription(patient_id=patients[5].patient_id, doctor_id=doctors[12].doctor_id, issue_date=date(2025, 5, 18), notes="For joint pain - Anti-inflammatory medication"),
        Prescription(patient_id=patients[6].patient_id, doctor_id=doctors[5].doctor_id, issue_date=date(2025, 5, 20), notes="Vitamin deficiency - Complete blood work needed"),
        Prescription(patient_id=patients[7].patient_id, doctor_id=doctors[15].doctor_id, issue_date=date(2025, 5, 22), notes="Pregnancy supplements - Follow up in 2 weeks"),
        Prescription(patient_id=patients[8].patient_id, doctor_id=doctors[18].doctor_id, issue_date=date(2025, 5, 25), notes="For anxiety and stress management"),
        Prescription(patient_id=patients[9].patient_id, doctor_id=doctors[20].doctor_id, issue_date=date(2025, 5, 28), notes="Eye infection - Use drops 4 times daily"),
        Prescription(patient_id=patients[0].patient_id, doctor_id=doctors[22].doctor_id, issue_date=date(2025, 6, 1), notes="Ear infection - Antibiotic course"),
        Prescription(patient_id=patients[2].patient_id, doctor_id=doctors[24].doctor_id, issue_date=date(2025, 6, 5), notes="Urinary tract infection - Complete course"),
        Prescription(patient_id=patients[4].patient_id, doctor_id=doctors[26].doctor_id, issue_date=date(2025, 6, 8), notes="Diabetes management - Check blood sugar"),
        Prescription(patient_id=patients[6].patient_id, doctor_id=doctors[28].doctor_id, issue_date=date(2025, 6, 10), notes="Thyroid medication - Annual checkup"),
        Prescription(patient_id=patients[8].patient_id, doctor_id=doctors[29].doctor_id, issue_date=date(2025, 6, 12), notes="Rheumatoid arthritis - Pain management"),
        Prescription(patient_id=patients[1].patient_id, doctor_id=doctors[2].doctor_id, issue_date=date(2025, 6, 15), notes="Chest pain - ECG recommended"),
        Prescription(patient_id=patients[3].patient_id, doctor_id=doctors[8].doctor_id, issue_date=date(2025, 6, 18), notes="Acne treatment - Use at night"),
        Prescription(patient_id=patients[5].patient_id, doctor_id=doctors[13].doctor_id, issue_date=date(2025, 6, 20), notes="Back pain - Physical therapy recommended"),
        Prescription(patient_id=patients[7].patient_id, doctor_id=doctors[16].doctor_id, issue_date=date(2025, 6, 22), notes="Prenatal vitamins - Monthly checkup"),
        Prescription(patient_id=patients[9].patient_id, doctor_id=doctors[21].doctor_id, issue_date=date(2025, 6, 25), notes="Glasses prescription - Eye exam done"),
    ]
    db.session.add_all(prescriptions)
    db.session.flush()
    
    # 6. Create Sales (30 sales)
    sales_data = [
        (patients[0], pharmacists[0], prescriptions[0], [(drugs[0], 2), (drugs[2], 1)]),
        (patients[1], pharmacists[1], prescriptions[1], [(drugs[10], 1), (drugs[29], 1)]),
        (patients[2], pharmacists[2], prescriptions[2], [(drugs[6], 1)]),
        (patients[3], pharmacists[0], prescriptions[3], [(drugs[30], 1), (drugs[38], 1)]),
        (patients[4], pharmacists[1], prescriptions[4], [(drugs[54], 2)]),
        (patients[5], pharmacists[2], None, [(drugs[1], 1), (drugs[4], 1)]),
        (patients[6], pharmacists[0], prescriptions[5], [(drugs[32], 1), (drugs[33], 1)]),
        (patients[0], pharmacists[1], None, [(drugs[40], 2)]),
        (patients[2], pharmacists[2], prescriptions[6], [(drugs[43], 1)]),
        (patients[4], pharmacists[0], None, [(drugs[14], 1), (drugs[15], 1)]),
        (patients[7], pharmacists[1], prescriptions[7], [(drugs[36], 1), (drugs[37], 1)]),
        (patients[8], pharmacists[2], prescriptions[8], [(drugs[58], 1)]),
        (patients[9], pharmacists[0], prescriptions[9], [(drugs[66], 1), (drugs[67], 1)]),
        (patients[1], pharmacists[1], None, [(drugs[20], 1)]),
        (patients[3], pharmacists[2], None, [(drugs[45], 2), (drugs[46], 1)]),
        (patients[5], pharmacists[0], prescriptions[10], [(drugs[8], 3)]),
        (patients[6], pharmacists[1], prescriptions[11], [(drugs[50], 1), (drugs[51], 1)]),
        (patients[8], pharmacists[2], None, [(drugs[55], 1)]),
        (patients[0], pharmacists[0], None, [(drugs[60], 2)]),
        (patients[2], pharmacists[1], prescriptions[12], [(drugs[70], 1), (drugs[71], 1)]),
        (patients[7], pharmacists[2], prescriptions[13], [(drugs[12], 1)]),
        (patients[9], pharmacists[0], prescriptions[14], [(drugs[23], 2)]),
        (patients[1], pharmacists[1], None, [(drugs[47], 1)]),
        (patients[4], pharmacists[2], prescriptions[15], [(drugs[34], 1)]),
        (patients[6], pharmacists[0], prescriptions[16], [(drugs[18], 2)]),
        (patients[0], pharmacists[1], prescriptions[17], [(drugs[5], 1)]),
        (patients[3], pharmacists[2], None, [(drugs[25], 1), (drugs[26], 1)]),
        (patients[5], pharmacists[0], prescriptions[18], [(drugs[52], 1)]),
        (patients[8], pharmacists[1], prescriptions[19], [(drugs[41], 2)]),
        (patients[2], pharmacists[2], None, [(drugs[64], 1), (drugs[65], 1)]),
    ]
    
    for patient, pharmacist, prescription, items in sales_data:
        total = sum(drug.price * qty for drug, qty in items)
        sale = Sale(
            patient_id=patient.patient_id,
            pharmacist_id=pharmacist.pharmacist_id,
            prescription_id=prescription.prescription_id if prescription else None,
            total_amount=total,
            sale_date=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        db.session.add(sale)
        db.session.flush()
        
        for drug, qty in items:
            detail = SaleDetails(
                sale_id=sale.sale_id,
                drug_id=drug.drug_id,
                quantity=qty,
                subtotal=drug.price * qty
            )
            db.session.add(detail)
            drug.stock_qty -= qty
    
    db.session.commit()
    print("✅ Sample data inserted successfully!")
    print(f"\n📊 Database Statistics:")
    print(f"   🧑‍⚕️ Doctors: {Doctor.query.count()}")
    print(f"   💊 Drugs: {Drug.query.count()}")
    print(f"   📋 Prescriptions: {Prescription.query.count()}")
    print(f"   💰 Sales: {Sale.query.count()}")
    print(f"   🧑‍🤝‍🧑 Patients: {Patient.query.count()}")
    print(f"   👥 Users: {User.query.count()}")
    print(f"   💊 Pharmacists: {Pharmacist.query.count()}")
    print("\n👥 User credentials:")
    print("   👑 admin / 123456 (Admin role - Full access)")
    print("   💊 pharmacist1 / 123456 (Pharmacist role)")
    print("   💊 pharmacist2 / 123456 (Pharmacist role)")