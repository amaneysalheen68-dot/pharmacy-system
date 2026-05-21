# PharmaCare - Pharmacy Management System

## Project Overview

PharmaCare is a complete web-based pharmacy management system built with Flask framework. The system helps pharmacies manage patients, doctors, drugs, prescriptions, and sales efficiently.

## Key Features

### For Admin
- Full control over all system data
- Add, edit, and delete patients, doctors, and drugs
- Manage pharmacist accounts
- View sales and inventory reports
- Create new admin or pharmacist users

### For Pharmacist
- Process sales with automatic stock updates
- Create prescriptions for patients
- View patient and doctor information
- Update drug stock quantities
- View sales history

## Technology Used

- Backend: Flask (Python)
- Database: SQLite with SQLAlchemy ORM
- Frontend: Bootstrap 5
- Authentication: Session-based with password hashing
- Containerization: Docker (Bonus)

## Database Structure

The system uses 7 tables:
1. User - Stores admin and pharmacist accounts
2. Patient - Stores patient information
3. Doctor - Stores doctor information
4. Pharmacist - Stores pharmacist information
5. Drug - Stores drug inventory (100+ drugs)
6. Prescription - Stores electronic prescriptions
7. Sale - Stores sales transactions
8. Sale_Details - Stores individual items in each sale

## Installation Guide

### Prerequisites
- Python 3.11 or higher installed on your computer

### Step 1: Download or Clone the Project

If you have Git installed:
git clone https://github.com/amaneysalheen68-dot/pharmacy-system.git
cd pharmacy-system

If you don't have Git, just download the project files as ZIP and extract them.

### Step 2: Install Required Libraries

Open terminal/command prompt in the project folder and run:

Or install all libraries from requirements.txt:

### Step 3: Run the Application

### Step 4: Open Your Browser

Go to: http://localhost:5000

## Login Credentials

After first run, you can login with these accounts:

Admin Account (Full Access):
- Username: admin
- Password: 123456

Pharmacist Accounts (Limited Access):
- Username: pharmacist1
- Password: 123456

- Username: pharmacist2
- Password: 123456

## Docker Setup (Optional Bonus)

If you have Docker installed:

Build the image:

Run the container:
docker run -p 5000:5000 pharmacy-system

## Sample Data Included

When you run the application for the first time, it automatically creates:

- 30 doctors in different specializations
- 100+ drugs in 12 categories
- 10 patients
- 4 pharmacists
- 20 prescriptions
- 30 sales transactions


## Available Pages

- Dashboard - Main page with statistics
- Patients - View and manage patients
- Doctors - View and manage doctors
- Pharmacists - Manage pharmacists (admin only)
- Drugs - View and manage drug inventory
- Prescriptions - Create and view prescriptions
- Sales - Process and view sales
- Reports - View sales and inventory reports (admin only)
- Users - Manage system users (admin only)

## User Permissions

Admin can:
- Add, edit, delete any data
- Create new users
- View all reports
- Access all pages

Pharmacist can:
- View patients and doctors
- Process sales
- Create prescriptions
- Update drug stock
- Cannot delete data
- Cannot access reports and user management

## API Endpoint

The system includes one API endpoint:

GET /api/sales_summary

Returns JSON with total sales, transaction count, and current date.

## Common Issues and Solutions

Issue: Database error about duplicate license numbers

Solution: Delete the pharmacy.db file and run the application again.

Issue: Port 5000 already in use

Solution: Change the port in app.py from 5000 to another number like 5001.

Issue: Module not found errors

Solution: Make sure you installed all required libraries with pip install -r requirements.txt

## How to Contribute

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Commit your changes
5. Push to your branch
6. Open a pull request

## License

This project is for educational purposes as part of a faculty assignment.

## Contact

GitHub: amaneysalheen68-dot
Project Link: https://github.com/amaneysalheen68-dot/pharmacy-system

## Acknowledgments

- Flask Framework
- Bootstrap Team
- SQLAlchemy
- All team members

---

Made with Python and Flask for the Web Application Development Course