ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 10 * 1024 * 1024 # 10 MB

BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
RELATIONSHIPS = ['Self', 'Spouse', 'Child', 'Parent', 'Sibling', 'Other']
GENDERS = ['Male', 'Female', 'Other']
RECORD_TYPES = ['General', 'Prescription', 'Test Report', 'Surgery', 'Discharge Summary', 'Other']
EXPENSE_CATEGORIES = ['Consultation', 'Medicines', 'Tests', 'Hospitalization', 'Insurance Premium', 'Other']
PAYMENT_METHODS = ['Cash', 'Credit Card', 'Debit Card', 'UPI', 'Insurance', 'Other']
HEALTH_PARAMETERS = {
    'Blood Pressure': 'mmHg',
    'Blood Sugar': 'mg/dL',
    'Weight': 'kg',
    'Height': 'cm',
    'Temperature': 'F',
    'Heart Rate': 'bpm',
    'Oxygen Level': '%'
}
MEDICINE_STATUSES = ['active', 'completed', 'stopped']
APPOINTMENT_STATUSES = ['upcoming', 'completed', 'cancelled']
REMINDER_STATUSES = ['pending', 'completed', 'missed']
CLAIM_STATUSES = ['submitted', 'in_progress', 'approved', 'rejected']
NOTIFICATION_TYPES = ['reminder', 'appointment', 'insurance', 'system']
