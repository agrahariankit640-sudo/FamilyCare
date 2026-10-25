from functools import wraps
from flask import jsonify, request, abort
from flask_login import current_user

def login_required_api(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def ownership_required(model_func):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resource_id = kwargs.get(list(kwargs.keys())[0]) if kwargs else None
            if resource_id:
                resource = model_func(resource_id, current_user.id)
                if not resource:
                    return jsonify({'error': 'Resource not found or unauthorized'}), 404
            return f(*args, **kwargs)
        return decorated_function
    return decorator
