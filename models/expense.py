from models.db import get_db

class Expense:
    @staticmethod
    def get_all(user_id, member_id=None, category=None, date_from=None, date_to=None):
        db = get_db()
        query = """
            SELECT e.*, fm.name as member_name 
            FROM expenses e 
            LEFT JOIN family_members fm ON e.family_member_id = fm.id 
            WHERE e.user_id = ?
        """
        values = [user_id]
        
        if member_id:
            query += " AND e.family_member_id = ?"
            values.append(member_id)
        if category:
            query += " AND LOWER(e.category) = LOWER(?)"
            values.append(category)
        if date_from:
            query += " AND e.expense_date >= ?"
            values.append(date_from)
        if date_to:
            query += " AND e.expense_date <= ?"
            values.append(date_to)
            
        query += " ORDER BY e.expense_date DESC"
        return db.execute(query, values).fetchall()
        
    @staticmethod
    def get_by_id(exp_id, user_id):
        db = get_db()
        return db.execute('''
            SELECT e.*, fm.name as member_name 
            FROM expenses e 
            LEFT JOIN family_members fm ON e.family_member_id = fm.id 
            WHERE e.id = ? AND e.user_id = ?
        ''', (exp_id, user_id)).fetchone()
        
    @staticmethod
    def create(user_id, data):
        db = get_db()
        data = dict(data)
        data['user_id'] = user_id
        if 'member_id' in data and not data.get('family_member_id'):
            data['family_member_id'] = data['member_id']
        if 'hospital_name' in data and not data.get('hospital'):
            data['hospital'] = data['hospital_name']
            
        fields = ['family_member_id', 'user_id', 'expense_date', 'amount', 'currency', 'category', 'hospital', 'description', 'document_id', 'payment_method', 'notes']
        
        insert_fields = []
        values = []
        placeholders = []
        
        for field in fields:
            if field in data and data[field] is not None and data[field] != '':
                insert_fields.append(field)
                values.append(data[field])
                placeholders.append('?')
                
        query = f"INSERT INTO expenses ({', '.join(insert_fields)}) VALUES ({', '.join(placeholders)})"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.lastrowid
        
    @staticmethod
    def update(exp_id, user_id, data):
        db = get_db()
        data = dict(data)
        if 'member_id' in data and not data.get('family_member_id'):
            data['family_member_id'] = data['member_id']
        if 'hospital_name' in data and not data.get('hospital'):
            data['hospital'] = data['hospital_name']
            
        allowed = ['family_member_id', 'expense_date', 'amount', 'currency', 'category', 'hospital', 'description', 'document_id', 'payment_method', 'notes']
        fields = []
        values = []
        
        for k, v in data.items():
            if k in allowed:
                fields.append(f"{k} = ?")
                values.append(v)
                
        if not fields:
            return False
            
        values.extend([exp_id, user_id])
        query = f"UPDATE expenses SET {', '.join(fields)} WHERE id = ? AND user_id = ?"
        db.execute(query, values)
        db.commit()
        return True
        
    @staticmethod
    def delete(exp_id, user_id):
        db = get_db()
        db.execute('DELETE FROM expenses WHERE id = ? AND user_id = ?', (exp_id, user_id))
        db.commit()
        return True
        
    @staticmethod
    def get_monthly_summary(user_id):
        db = get_db()
        return db.execute('''
            SELECT strftime('%Y-%m', expense_date) as month, SUM(amount) as total 
            FROM expenses 
            WHERE user_id = ? 
            GROUP BY strftime('%Y-%m', expense_date) 
            ORDER BY month DESC LIMIT 12
        ''', (user_id,)).fetchall()
        
    @staticmethod
    def get_category_summary(user_id):
        db = get_db()
        return db.execute('''
            SELECT category, SUM(amount) as total 
            FROM expenses 
            WHERE user_id = ? 
            GROUP BY category 
            ORDER BY total DESC
        ''', (user_id,)).fetchall()
        
    @staticmethod
    def get_total(user_id):
        db = get_db()
        result = db.execute('SELECT SUM(amount) as total FROM expenses WHERE user_id = ?', (user_id,)).fetchone()
        return result['total'] if result and result['total'] else 0
