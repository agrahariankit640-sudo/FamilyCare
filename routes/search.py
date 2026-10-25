from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.search_service import search_all

search_bp = Blueprint('search', __name__)

@search_bp.route('/', methods=['GET'])
@login_required
def search():
    try:
        query = request.args.get('q', '')
        results = search_all(current_user.id, query, request.args)
        return jsonify({'success': True, 'data': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
