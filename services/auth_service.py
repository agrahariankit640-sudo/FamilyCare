from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
import os

from utils.validators import validate_email, validate_password, validate_phone

def register_user(name, email, phone, password):
    if not email or not validate_email(email):
        return None, "Invalid email format"
    if not password or not validate_password(password):
        return None, "Password must be at least 8 characters long and include uppercase, lowercase, numbers, and special characters"
    if phone and not validate_phone(phone):
        return None, "Invalid phone number format"

    existing_user = User.get_by_email(email)
    if existing_user:
        return None, "Email already registered"
    
    password_hash = generate_password_hash(password)
    user_id = User.create(name, email, phone, password_hash)
    return user_id, None


def authenticate_user(email, password):
    user = User.get_by_email(email)
    if not user:
        return None, "Invalid email or password"
    
    if not check_password_hash(user['password_hash'], password):
        return None, "Invalid email or password"
        
    if not user['is_active']:
        return None, "Account is disabled"
        
    return user, None

def update_profile(user_id, data):
    return User.update(user_id, data)

def change_password(user_id, old_password, new_password):
    user = User.get_by_id(user_id)
    if not user or not check_password_hash(user['password_hash'], old_password):
        return False, "Invalid old password"
        
    new_hash = generate_password_hash(new_password)
    User.update_password(user_id, new_hash)
    return True, None

def create_admin_if_not_exists():
    admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@familycare.com')
    admin_password = current_app.config.get('ADMIN_PASSWORD', 'Admin@123')
    
    if not User.get_by_email(admin_email):
        password_hash = generate_password_hash(admin_password)
        User.create("Admin", admin_email, "", password_hash, role="admin")
