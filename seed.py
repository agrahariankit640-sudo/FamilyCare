import os
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash
from app import create_app
from models.db import get_db

def run_seed():
    app = create_app()
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        print("Checking if demo user already exists...")
        cursor.execute("SELECT id FROM users WHERE email = ?", ('demo@familycare.com',))
        existing = cursor.fetchone()
        if existing:
            print("Demo user already exists (id = {}). Cleaning up previous demo data...".format(existing['id']))
            user_id = existing['id']
            cursor.execute("DELETE FROM family_members WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM medical_records WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM medicines WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM medicine_reminders WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM doctor_visits WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM tests WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM vaccinations WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM health_parameters WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM expenses WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM insurance_policies WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM insurance_claims WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM notifications WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM audit_logs WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            db.commit()

        print("Creating demo user: Rajesh Sharma (demo@familycare.com)...")
        pw_hash = generate_password_hash('Demo@123')
        cursor.execute("""
            INSERT INTO users (name, email, phone, password_hash, role, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        """, ('Rajesh Sharma', 'demo@familycare.com', '+91 9876543210', pw_hash, 'user'))
        user_id = cursor.lastrowid

        print("Adding family members...")
        members_data = [
            ('Rajesh Sharma', 'Self', 'Male', '1985-03-15', 'B+', '+91 9876543210', 'rajesh@example.com',
             'Flat 402, Shanti Heights, Mumbai', 'Priya Sharma', '+91 9876543211',
             'Penicillin', 'Mild hypertension', 'Prefers morning appointments'),
            ('Priya Sharma', 'Wife', 'Female', '1988-07-22', 'A+', '+91 9876543211', 'priya@example.com',
             'Flat 402, Shanti Heights, Mumbai', 'Rajesh Sharma', '+91 9876543210',
             'None', 'None', 'Annual checkup due every May'),
            ('Aarav Sharma', 'Son', 'Male', '2015-11-10', 'B+', '+91 9876543210', 'aarav@example.com',
             'Flat 402, Shanti Heights, Mumbai', 'Rajesh Sharma', '+91 9876543210',
             'Dust, Pollen', 'Seasonal Asthma', 'School vaccination records updated'),
            ('Kavita Sharma', 'Mother', 'Female', '1958-01-05', 'O+', '+91 9876543212', 'kavita@example.com',
             'Flat 402, Shanti Heights, Mumbai', 'Rajesh Sharma', '+91 9876543210',
             'Sulfa drugs', 'Type 2 Diabetes, Osteoarthritis', 'Requires low-sodium diet and regular blood sugar checks')
        ]

        member_ids = {}
        for m in members_data:
            cursor.execute("""
                INSERT INTO family_members (
                    user_id, name, relationship, gender, date_of_birth, blood_group,
                    phone, email, address, emergency_contact, emergency_contact_phone,
                    allergies, existing_conditions, important_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7], m[8], m[9], m[10], m[11], m[12]))
            member_ids[m[0]] = cursor.lastrowid

        rajesh_id = member_ids['Rajesh Sharma']
        priya_id = member_ids['Priya Sharma']
        aarav_id = member_ids['Aarav Sharma']
        kavita_id = member_ids['Kavita Sharma']

        print("Adding medical records...")
        records_data = [
            (rajesh_id, user_id, 'Complete Blood Count & Lipid Profile', 'Lab Test', '2026-06-15', 'Dr. Anand Patel', 'Apollo Hospital', 'Routine corporate health checkup panel', 'Borderline cholesterol', 'Follow up after 3 months', 'blood,lipids,routine'),
            (rajesh_id, user_id, 'Chest X-Ray PA View', 'Scan', '2026-07-20', 'Dr. Sanjay Mehta', 'City Diagnostic Center', 'Mild cough evaluation - clear lungs reported', 'Normal chest radiograph', 'No treatment required', 'xray,lungs'),
            (priya_id, user_id, 'Annual Health Checkup & Pap Smear', 'Medical Report', '2026-05-10', 'Dr. Meera Reddy', 'Fortis Hospital', 'Comprehensive wellness checkup', 'All parameters normal', 'Repeat annually', 'wellness,annual'),
            (aarav_id, user_id, 'Pediatric Allergy Assessment', 'Allergy', '2026-07-25', 'Dr. Suresh Kumar', 'Lilavati Children Clinic', 'Skin prick test for seasonal allergic rhinitis', 'Dust mite sensitivity', 'Prescribed antihistamine as needed', 'pediatric,allergy'),
            (kavita_id, user_id, 'Quarterly HbA1c & Diabetic Review', 'Lab Test', '2026-09-05', 'Dr. Rajan Nair', 'Max Healthcare', 'Quarterly glycated hemoglobin monitoring', 'HbA1c 7.2% - Moderately controlled', 'Increase walking and adjust Metformin', 'diabetes,hba1c'),
            (kavita_id, user_id, 'Ophthalmology Fundus Examination', 'Doctor Visit', '2026-04-18', 'Dr. Deepa Iyer', 'Eye Care Center', 'Diabetic retinopathy screening', 'No diabetic retinopathy detected', 'Yearly review recommended', 'eyes,screening'),
            (priya_id, user_id, 'Dental Scaling and Cavity Assessment', 'Doctor Visit', '2026-03-12', 'Dr. Priya Menon', 'Smile Dental Clinic', 'Routine dental hygiene checkup', 'Mild gingivitis treated', 'Brush twice daily, mouthwash', 'dental,hygiene'),
            (aarav_id, user_id, 'Routine Growth & Vaccination Review', 'Vaccination', '2026-08-01', 'Dr. Suresh Kumar', 'Lilavati Children Clinic', 'Growth percentiles: 50th for height, 55th for weight', 'Healthy growth milestones', 'Administered DPT booster', 'pediatric,growth')
        ]
        for r in records_data:
            cursor.execute("""
                INSERT INTO medical_records (
                    family_member_id, user_id, title, record_type, record_date,
                    doctor, hospital, description, diagnosis, notes, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, r)

        print("Adding medicines...")
        medicines_data = [
            (rajesh_id, user_id, 'Amlodipine 5mg', '5mg', 'Once daily', '2026-01-01', '2026-12-31', 'Morning (8:00 AM)', 'Take after breakfast with water', 'Dr. Anand Patel', 'For BP management', 'active'),
            (kavita_id, user_id, 'Metformin 500mg', '500mg', 'Twice daily', '2025-06-01', '2026-12-31', 'Morning & Evening', 'Take with meals to avoid stomach upset', 'Dr. Rajan Nair', 'Type 2 Diabetes maintenance', 'active'),
            (kavita_id, user_id, 'Calcium + Vitamin D3', '500mg/250IU', 'Once daily', '2026-02-01', '2026-12-31', 'Noon (After Lunch)', 'Take after meal', 'Dr. Rajan Nair', 'Bone density support', 'active'),
            (aarav_id, user_id, 'Cetirizine Syrup 5ml', '5ml', 'As needed', '2026-07-25', '2026-10-31', 'Night (Before bed)', 'Take only when allergic symptoms or sneezing arise', 'Dr. Suresh Kumar', 'Allergy relief', 'active'),
            (priya_id, user_id, 'Multivitamin & Zinc Capsule', '1 Capsule', 'Once daily', '2026-05-10', '2026-11-10', 'Morning', 'Take after breakfast', 'Dr. Meera Reddy', 'General wellness supplement', 'active'),
            (kavita_id, user_id, 'Glucosamine Sulfate 750mg', '750mg', 'Once daily', '2026-03-01', '2026-09-01', 'Morning', 'For joint lubrication and stiffness', 'Dr. Rajan Nair', 'Completed course', 'completed')
        ]
        med_ids = []
        for med in medicines_data:
            cursor.execute("""
                INSERT INTO medicines (
                    family_member_id, user_id, name, dosage, frequency,
                    start_date, end_date, time_of_day, instructions, doctor, notes, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, med)
            med_ids.append(cursor.lastrowid)

        print("Adding medicine reminders...")
        today = date.today().isoformat()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        cursor.execute("""
            INSERT INTO medicine_reminders (medicine_id, family_member_id, user_id, reminder_date, reminder_time, frequency, status)
            VALUES (?, ?, ?, ?, ?, 'daily', 'pending')
        """, (med_ids[0], rajesh_id, user_id, today, '08:00'))
        cursor.execute("""
            INSERT INTO medicine_reminders (medicine_id, family_member_id, user_id, reminder_date, reminder_time, frequency, status)
            VALUES (?, ?, ?, ?, ?, 'daily', 'pending')
        """, (med_ids[1], kavita_id, user_id, today, '08:30'))
        cursor.execute("""
            INSERT INTO medicine_reminders (medicine_id, family_member_id, user_id, reminder_date, reminder_time, frequency, status)
            VALUES (?, ?, ?, ?, ?, 'daily', 'pending')
        """, (med_ids[1], kavita_id, user_id, today, '20:30'))
        cursor.execute("""
            INSERT INTO medicine_reminders (medicine_id, family_member_id, user_id, reminder_date, reminder_time, frequency, status)
            VALUES (?, ?, ?, ?, ?, 'daily', 'taken')
        """, (med_ids[4], priya_id, user_id, today, '09:00'))

        print("Adding doctor appointments...")
        appts = [
            (rajesh_id, user_id, 'Dr. Anand Patel', 'Apollo Hospital', 'Cardiology', '2026-08-15', '10:00', 'BP review & cholesterol management', 'BP well-controlled at 126/80', '2026-11-15', 'completed'),
            (priya_id, user_id, 'Dr. Meera Reddy', 'Fortis Hospital', 'General Medicine', '2026-05-10', '11:30', 'Routine annual medical checkup', 'Prescribed multivitamin', None, 'completed'),
            (aarav_id, user_id, 'Dr. Suresh Kumar', 'Lilavati Children Clinic', 'Pediatrics', (date.today() + timedelta(days=14)).isoformat(), '16:00', 'Quarterly asthma follow-up and growth check', 'Bring symptom diary', None, 'upcoming'),
            (kavita_id, user_id, 'Dr. Rajan Nair', 'Max Healthcare', 'Endocrinology', (date.today() + timedelta(days=19)).isoformat(), '11:00', 'Diabetic HbA1c quarterly review', 'Fasting blood glucose test on same morning', (date.today() + timedelta(days=90)).isoformat(), 'upcoming'),
            (kavita_id, user_id, 'Dr. Deepa Iyer', 'Eye Care Center', 'Ophthalmology', '2026-04-18', '09:30', 'Diabetic retinopathy screening', 'Retina clean and healthy', '2027-04-18', 'completed')
        ]
        for a in appts:
            cursor.execute("""
                INSERT INTO doctor_visits (
                    family_member_id, user_id, doctor_name, hospital, specialization,
                    visit_date, visit_time, reason, notes, follow_up_date, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, a)

        print("Adding medical tests...")
        tests_data = [
            (rajesh_id, user_id, 'Complete Blood Count (CBC)', '2026-06-15', 'Dr. Anand Patel', 'Hemoglobin 14.8, WBC 6500, Platelets normal', None, 'Normal results'),
            (rajesh_id, user_id, 'Lipid Profile Panel', '2026-06-15', 'Dr. Anand Patel', 'Total Cholesterol 210 mg/dL, HDL 45, LDL 135', '2026-11-15', 'Diet modifications suggested'),
            (kavita_id, user_id, 'Glycated Hemoglobin (HbA1c)', '2026-09-05', 'Dr. Rajan Nair', 'HbA1c 7.2% (Target < 7.0%)', (date.today() + timedelta(days=60)).isoformat(), 'Monitor fasting glucose closely'),
            (priya_id, user_id, 'Thyroid Stimulating Hormone (TSH)', '2026-05-10', 'Dr. Meera Reddy', 'TSH: 2.8 uIU/mL (Normal range 0.4-4.0)', None, 'Euthyroid state confirmed')
        ]
        for t in tests_data:
            cursor.execute("""
                INSERT INTO tests (
                    family_member_id, user_id, test_name, test_date, doctor,
                    result_summary, follow_up_date, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, t)

        print("Adding vaccinations...")
        vaxes = [
            (rajesh_id, user_id, 'COVID-19 Precaution Dose (Covishield)', '2026-01-15', 3, None, 'Apollo Hospital', 'Booster dose completed without side effects'),
            (priya_id, user_id, 'COVID-19 Precaution Dose (Covaxin)', '2026-01-20', 3, None, 'Fortis Hospital', 'Mild fever for 24 hours resolved with paracetamol'),
            (aarav_id, user_id, 'DPT Booster Dose', '2026-08-01', 5, None, 'Lilavati Children Clinic', 'Administered on schedule'),
            (aarav_id, user_id, 'Typhoid Conjugate Vaccine', (date.today() + timedelta(days=45)).isoformat(), 2, None, 'Lilavati Children Clinic', 'Upcoming scheduled dose'),
            (kavita_id, user_id, 'Influenza (Quadrivalent Flu Vaccine)', '2026-09-01', 1, (date.today() + timedelta(days=365)).isoformat(), 'Max Healthcare', 'Annual geriatric flu protection')
        ]
        for v in vaxes:
            cursor.execute("""
                INSERT INTO vaccinations (
                    family_member_id, user_id, vaccine_name, vaccination_date, dose_number,
                    next_dose_date, hospital, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, v)

        print("Adding health parameters history...")
        params_data = [
            # Rajesh BP
            (rajesh_id, user_id, 'Blood Pressure', '130/85', 'mmHg', '2026-06-15', '08:00', 'Morning reading'),
            (rajesh_id, user_id, 'Blood Pressure', '128/82', 'mmHg', '2026-07-20', '08:30', 'Normal reading'),
            (rajesh_id, user_id, 'Blood Pressure', '132/84', 'mmHg', '2026-08-15', '09:00', 'Post clinic visit'),
            (rajesh_id, user_id, 'Blood Pressure', '126/80', 'mmHg', '2026-09-10', '08:15', 'Target reached'),
            # Rajesh Weight
            (rajesh_id, user_id, 'Weight', '78.5', 'kg', '2026-06-15', '07:30', 'Initial baseline'),
            (rajesh_id, user_id, 'Weight', '77.8', 'kg', '2026-07-20', '07:30', 'Diet progress'),
            (rajesh_id, user_id, 'Weight', '77.0', 'kg', '2026-08-15', '07:30', 'Regular gym workout'),
            (rajesh_id, user_id, 'Weight', '76.2', 'kg', '2026-09-10', '07:30', 'Weight down 2.3kg'),
            # Kavita Blood Sugar Fasting
            (kavita_id, user_id, 'Blood Sugar', '145', 'mg/dL', '2026-06-10', '07:00', 'Fasting reading'),
            (kavita_id, user_id, 'Blood Sugar', '138', 'mg/dL', '2026-07-15', '07:00', 'Fasting reading'),
            (kavita_id, user_id, 'Blood Sugar', '142', 'mg/dL', '2026-08-20', '07:00', 'Fasting reading'),
            (kavita_id, user_id, 'Blood Sugar', '132', 'mg/dL', '2026-09-05', '07:00', 'Pre-doctor test'),
            # Priya Heart Rate
            (priya_id, user_id, 'Heart Rate', '72', 'bpm', '2026-06-01', '08:00', 'Resting pulse'),
            (priya_id, user_id, 'Heart Rate', '70', 'bpm', '2026-07-01', '08:00', 'Resting pulse'),
            (priya_id, user_id, 'Heart Rate', '74', 'bpm', '2026-08-01', '08:00', 'Post-yoga pulse'),
            (priya_id, user_id, 'Heart Rate', '71', 'bpm', '2026-09-01', '08:00', 'Resting pulse'),
            # Kavita SpO2
            (kavita_id, user_id, 'SpO2', '98', '%', '2026-08-15', '10:00', 'Normal saturation'),
            (kavita_id, user_id, 'SpO2', '97', '%', '2026-09-05', '10:00', 'Normal saturation'),
            # Aarav Temperature
            (aarav_id, user_id, 'Temperature', '98.6', '°F', '2026-09-12', '12:00', 'Normal temperature')
        ]
        for p in params_data:
            cursor.execute("""
                INSERT INTO health_parameters (
                    family_member_id, user_id, parameter_name, value, unit,
                    record_date, record_time, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, p)

        print("Adding medical expenses...")
        expenses_data = [
            (rajesh_id, user_id, '2026-08-15', 1500.00, 'Doctor Consultation', 'Apollo Hospital', 'Cardiology specialist consultation fee', 'UPI', 'Paid via GooglePay'),
            (rajesh_id, user_id, '2026-06-15', 2200.00, 'Test', 'Apollo Diagnostics', 'Full body lipid and blood biochemistry', 'Credit Card', 'HDFC Card'),
            (kavita_id, user_id, '2026-09-01', 3250.00, 'Medicine', 'Apollo Pharmacy', 'Monthly diabetes and calcium refills', 'Debit Card', 'Monthly routine'),
            (priya_id, user_id, '2026-05-10', 800.00, 'Doctor Consultation', 'Fortis Hospital', 'General physician wellness fee', 'Cash', 'Receipt saved'),
            (priya_id, user_id, '2026-03-12', 2500.00, 'Dental', 'Smile Dental Clinic', 'Ultrasonic dental scaling and polish', 'UPI', 'Paid via PhonePe'),
            (aarav_id, user_id, '2026-08-01', 1200.00, 'Vaccination', 'Lilavati Clinic', 'DPT Booster administration', 'UPI', 'Paid via Paytm'),
            (kavita_id, user_id, '2026-04-18', 1000.00, 'Doctor Consultation', 'Eye Care Center', 'Comprehensive dilated fundus exam', 'Cash', 'No treatment required'),
            (rajesh_id, user_id, '2026-09-01', 450.00, 'Medicine', 'MedPlus Chemist', 'Amlodipine 3-month supply', 'UPI', 'Generic brand savings'),
            (kavita_id, user_id, '2026-09-05', 650.00, 'Test', 'Max Pathology', 'HbA1c test fee', 'Debit Card', 'Quarterly check'),
            (kavita_id, user_id, '2026-07-10', 4800.00, 'Hospital', 'Max Healthcare Daycare', 'Knee joint physical therapy session', 'Credit Card', 'Physiotherapy rehab')
        ]
        for e in expenses_data:
            cursor.execute("""
                INSERT INTO expenses (
                    family_member_id, user_id, expense_date, amount, category,
                    hospital, description, payment_method, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, e)

        print("Adding insurance policies & claims...")
        cursor.execute("""
            INSERT INTO insurance_policies (
                family_member_id, user_id, provider, policy_number, policy_holder,
                start_date, expiry_date, coverage_amount, premium, contact_info, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (rajesh_id, user_id, 'Star Health Family Optima', 'SH-2024-78901', 'Rajesh Sharma',
              '2024-04-01', '2027-03-31', 1000000.00, 18500.00, '1800-425-2255 / support@starhealth.in',
              'Comprehensive family floater covering self, spouse, and child.'))
        policy_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO insurance_policies (
                family_member_id, user_id, provider, policy_number, policy_holder,
                start_date, expiry_date, coverage_amount, premium, contact_info, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (kavita_id, user_id, 'LIC Senior Citizen Health Plus', 'LIC-2023-45678', 'Rajesh Sharma',
              '2023-07-01', (date.today() + timedelta(days=20)).isoformat(), 500000.00, 14200.00,
              '022-68276827 / branch402@licindia.com', 'Senior citizen plan. Expiry approaching in 20 days! Renewal required.'))
        lic_policy_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO insurance_claims (
                policy_id, user_id, claim_number, claim_date, amount,
                hospital, status, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (policy_id, user_id, 'CLM-STAR-2026-001', '2026-07-12', 4800.00,
              'Max Healthcare Daycare', 'approved', 'Reimbursement for knee physiotherapy sessions and rehab treatment.'))

        print("Adding notifications...")
        notifications_data = [
            (user_id, 'medicine', 'Morning Medicine Due', 'Rajesh Sharma: Amlodipine 5mg scheduled at 08:00 AM', '/reminders', 0),
            (user_id, 'appointment', 'Upcoming Appointment in 2 Weeks', 'Aarav Sharma: Pediatric asthma review with Dr. Suresh Kumar', '/appointments', 0),
            (user_id, 'insurance', 'Insurance Policy Expiring Soon', 'LIC Senior Citizen Plan for Kavita Sharma expires in 20 days. Please renew.', '/insurance', 0),
            (user_id, 'test', 'Follow-up Test Pending', 'Kavita Sharma: HbA1c review test due in 60 days', '/tests', 1),
            (user_id, 'vaccination', 'Upcoming Vaccination Scheduled', 'Aarav Sharma: Typhoid Conjugate Vaccine scheduled', '/vaccinations', 0)
        ]
        for n in notifications_data:
            cursor.execute("""
                INSERT INTO notifications (user_id, type, title, message, link, is_read)
                VALUES (?, ?, ?, ?, ?, ?)
            """, n)

        print("Adding audit logs...")
        cursor.execute("""
            INSERT INTO audit_logs (user_id, action, entity_type, details)
            VALUES (?, 'login', 'auth', 'User Rajesh Sharma logged in successfully')
        """, (user_id,))
        cursor.execute("""
            INSERT INTO audit_logs (user_id, action, entity_type, details)
            VALUES (?, 'create_member', 'family_members', 'Added 4 family members to profile')
        """, (user_id,))
        cursor.execute("""
            INSERT INTO audit_logs (user_id, action, entity_type, details)
            VALUES (?, 'create_record', 'medical_records', 'Logged annual health report and lab panels')
        """, (user_id,))

        db.commit()

        print("\n" + "="*50)
        print("DEMO DATA SEEDED SUCCESSFULLY!")
        print("="*50)
        print("Demo User Login:")
        print("  Email:    demo@familycare.com")
        print("  Password: Demo@123")
        print("Admin User Login:")
        print("  Email:    admin@familycare.com")
        print("  Password: Admin@123")
        print("="*50 + "\n")

if __name__ == '__main__':
    run_seed()
