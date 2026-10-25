import uuid
from datetime import datetime
from utils.constants import ALLOWED_EXTENSIONS

def generate_filename(original):
    ext = original.rsplit('.', 1)[1].lower() if '.' in original else ''
    return f"{uuid.uuid4().hex}.{ext}"

def format_date(date_obj):
    if isinstance(date_obj, str):
        return date_obj
    if date_obj:
        return date_obj.strftime('%Y-%m-%d')
    return None

def format_datetime(dt_obj):
    if isinstance(dt_obj, str):
        return dt_obj
    if dt_obj:
        return dt_obj.strftime('%Y-%m-%d %H:%M:%S')
    return None

def paginate_query(query, page, per_page):
    offset = (page - 1) * per_page
    paginated_query = f"{query} LIMIT {per_page} OFFSET {offset}"
    return paginated_query

def get_age(date_of_birth):
    if not date_of_birth:
        return None
    if isinstance(date_of_birth, str):
        dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
    else:
        dob = date_of_birth
    today = datetime.today().date()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
