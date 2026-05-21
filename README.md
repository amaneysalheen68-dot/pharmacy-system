# Pharmacy Management System

A complete Flask web application for managing pharmacy operations including patients, doctors, pharmacists, drug inventory, prescriptions, and sales transactions.

## Team Members
- 5-7 members (adjust as needed)

## Features
- ✅ Patient Management
- ✅ Doctor Management  
- ✅ Pharmacist Management
- ✅ Drug Inventory with Stock Tracking
- ✅ Prescription Management
- ✅ Sales Processing with Automatic Stock Update
- ✅ Reports & Analytics Dashboard
- ✅ Low Stock Alerts
- ✅ REST API Endpoint

## Database Schema (7 Tables)
- Patient
- Doctor
- Pharmacist
- Drug
- Prescription
- Sale
- Sale_Details

## Endpoints (8+)
1. `/` - Dashboard
2. `/patients` - Manage patients
3. `/doctors` - Manage doctors
4. `/pharmacists` - Manage pharmacists
5. `/drugs` - Manage inventory
6. `/prescriptions` - Manage prescriptions
7. `/sales` - Process sales
8. `/reports` - View reports
9. `/api/sales_summary` - REST API

## Installation

### Local Setup
```bash
git clone <your-repo-url>
cd pharmacy_system
pip install -r requirements.txt
python app.py