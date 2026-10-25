from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.expense import Expense
from models.audit_log import AuditLog
from datetime import datetime

expenses_bp = Blueprint('expenses', __name__)

CURRENCY_RATES = {
    'USD': 1.0,
    'INR': 83.5,
    'EUR': 0.92,
    'GBP': 0.79,
    'AED': 3.67,
    'CAD': 1.36,
    'AUD': 1.52
}

def convert_amount(amount, from_curr, to_curr):
    try:
        val = float(amount or 0)
    except (ValueError, TypeError):
        return 0.0
    from_r = CURRENCY_RATES.get((from_curr or 'USD').upper(), 1.0)
    to_r = CURRENCY_RATES.get((to_curr or 'USD').upper(), 1.0)
    in_usd = val / from_r
    return in_usd * to_r

@expenses_bp.route('/', methods=['GET'])
@login_required
def get_all():
    try:
        member_id = request.args.get('family_member_id') or request.args.get('member_id')
        category = request.args.get('category')
        date_from = request.args.get('date_from') or request.args.get('from')
        date_to = request.args.get('date_to') or request.args.get('to')
        target_curr = (request.args.get('currency') or getattr(current_user, 'currency', None) or 'USD').upper()
        
        items = Expense.get_all(current_user.id, member_id=member_id, category=category, date_from=date_from, date_to=date_to)
        result = []
        for it in items:
            d = dict(it)
            curr = d.get('currency') or 'USD'
            d['currency'] = curr
            d['converted_amount'] = round(convert_amount(d['amount'], curr, target_curr), 2)
            d['display_currency'] = target_curr
            result.append(d)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expenses_bp.route('/', methods=['POST'])
@login_required
def create():
    try:
        data = dict(request.json)
        if not data.get('currency'):
            data['currency'] = getattr(current_user, 'currency', None) or 'USD'
        item_id = Expense.create(current_user.id, data)
        if item_id:
            AuditLog.log(current_user.id, 'create_expense', f'Created Expense {item_id}')
            return jsonify({'success': True, 'data': {'id': item_id}})
        return jsonify({'error': 'Creation failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expenses_bp.route('/<int:id>', methods=['GET'])
@login_required
def get(id):
    try:
        item = Expense.get_by_id(id, current_user.id)
        if item:
            d = dict(item)
            if not d.get('currency'):
                d['currency'] = 'USD'
            return jsonify({'success': True, 'data': d})
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expenses_bp.route('/<int:id>', methods=['PUT'])
@login_required
def update(id):
    try:
        data = request.json
        success = Expense.update(id, current_user.id, data)
        if success:
            AuditLog.log(current_user.id, 'update_expense', f'Updated Expense {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Update failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expenses_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete(id):
    try:
        success = Expense.delete(id, current_user.id)
        if success:
            AuditLog.log(current_user.id, 'delete_expense', f'Deleted Expense {id}')
            return jsonify({'success': True})
        return jsonify({'error': 'Deletion failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expenses_bp.route('/summary', methods=['GET'])
@login_required
def summary():
    try:
        target_curr = (request.args.get('currency') or getattr(current_user, 'currency', None) or 'USD').upper()
        all_expenses = Expense.get_all(current_user.id)
        
        current_m = datetime.now().strftime('%Y-%m')
        this_month_total = 0.0
        total_all_time = 0.0
        monthly_map = {}
        category_map = {}
        
        for it in all_expenses:
            amt = float(it['amount'] or 0)
            orig_curr = it['currency'] if ('currency' in it.keys() and it['currency']) else 'USD'
            converted = convert_amount(amt, orig_curr, target_curr)
            
            total_all_time += converted
            
            # Month
            exp_date_str = str(it['expense_date']) if it['expense_date'] else ''
            m_key = exp_date_str[:7] if len(exp_date_str) >= 7 else current_m
            monthly_map[m_key] = monthly_map.get(m_key, 0.0) + converted
            if m_key == current_m:
                this_month_total += converted
                
            # Category
            cat_key = it['category'] or 'Other'
            category_map[cat_key] = category_map.get(cat_key, 0.0) + converted

        # Sort months chronologically for trend
        sorted_months = sorted(monthly_map.keys())[-12:]
        trend_labels = sorted_months
        trend_values = [round(monthly_map[m], 2) for m in sorted_months]
        
        # Sort categories by total desc
        sorted_cats = sorted(category_map.items(), key=lambda x: x[1], reverse=True)
        top_cat = sorted_cats[0][0] if sorted_cats else '-'
        cat_labels = [c[0] for c in sorted_cats]
        cat_values = [round(c[1], 2) for c in sorted_cats]
        
        monthly_list = [{'month': m, 'total': round(monthly_map[m], 2)} for m in reversed(sorted_months)]
        cat_list = [{'category': c[0], 'total': round(c[1], 2)} for c in sorted_cats]
        
        return jsonify({
            'success': True,
            'data': {
                'currency': target_curr,
                'thisMonth': round(this_month_total, 2),
                'total': round(total_all_time, 2),
                'topCategory': top_cat,
                'monthly': monthly_list,
                'categories': cat_list,
                'trendData': {
                    'labels': trend_labels,
                    'datasets': [{
                        'label': f'Monthly Spending ({target_curr})',
                        'data': trend_values,
                        'backgroundColor': 'rgba(37, 99, 235, 0.6)'
                    }]
                },
                'categoryData': {
                    'labels': cat_labels,
                    'datasets': [{
                        'data': cat_values,
                        'backgroundColor': [
                            '#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#64748b'
                        ]
                    }]
                }
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
