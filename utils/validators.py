import re
from datetime import datetime
from utils.constants import ALLOWED_EXTENSIONS, MAX_FILE_SIZE

def validate_email(email):
    pattern = r'^[\w\.\+-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

def validate_phone(phone):
    pattern = r'^\+?[\d\s-]{10,20}$'
    return re.match(pattern, phone) is not None

def validate_date(date_str):
    try:
        datetime.fromisoformat(date_str)
        return True
    except ValueError:
        return False

def validate_file(filename, file_size):
    if file_size > MAX_FILE_SIZE:
        return False
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def sanitize_string(value):
    if not isinstance(value, str):
        return value
    value = value.strip()
    value = value.replace('<', '&lt;').replace('>', '&gt;')
    return value

def validate_required(data, fields):
    missing = []
    for field in fields:
        if field not in data or data[field] is None or str(data[field]).strip() == '':
            missing.append(field)
    return len(missing) == 0, missing
