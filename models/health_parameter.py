from models.db import get_db

class HealthParameter:
    @staticmethod
    def get_all(user_id, member_id=None, parameter=None):
        db = get_db()
        query = """
            SELECT h.*, fm.name as member_name 
            FROM health_parameters h 
            LEFT JOIN family_members fm ON h.family_member_id = fm.id 
            WHERE h.user_id = ?
        """
        values = [user_id]
        
        if member_id:
            query += " AND h.family_member_id = ?"
            values.append(member_id)
        if parameter:
            query += " AND LOWER(h.parameter_name) = LOWER(?)"
            values.append(parameter)
            
        query += " ORDER BY h.record_date DESC, h.record_time DESC"
        return db.execute(query, values).fetchall()
        
    @staticmethod
    def create(user_id, data):
        db = get_db()
        data = dict(data)
        data['user_id'] = user_id
        
        if 'member_id' in data and not data.get('family_member_id'):
            data['family_member_id'] = data['member_id']
        if 'memberId' in data and not data.get('family_member_id'):
            data['family_member_id'] = data['memberId']
        if 'parameter_type' in data and not data.get('parameter_name'):
            data['parameter_name'] = data['parameter_type']
        if 'type' in data and not data.get('parameter_name'):
            data['parameter_name'] = data['type']
            
        if 'parameter_value' in data and not data.get('value'):
            data['value'] = data['parameter_value']
        if 'reading' in data and not data.get('value'):
            data['value'] = data['reading']
            
        reading_date = data.get('reading_date') or data.get('date')

        if reading_date and 'T' in str(reading_date):
            parts = str(reading_date).split('T')
            data['record_date'] = parts[0]
            data['record_time'] = parts[1]
        elif reading_date:
            data['record_date'] = str(reading_date)
            
        from datetime import datetime
        if not data.get('record_date'):
            data['record_date'] = datetime.now().strftime('%Y-%m-%d')
        if not data.get('record_time'):
            data['record_time'] = datetime.now().strftime('%H:%M')
            
        if not data.get('unit'):
            param = (data.get('parameter_name') or '').lower()
            if 'pressure' in param:
                data['unit'] = 'mmHg'
            elif 'sugar' in param:
                data['unit'] = 'mg/dL'
            elif 'rate' in param or 'pulse' in param:
                data['unit'] = 'bpm'
            elif 'weight' in param:
                data['unit'] = 'kg'
            elif 'temp' in param:
                data['unit'] = '°F'
            elif 'spo2' in param or 'oxygen' in param:
                data['unit'] = '%'
                
        fields = ['family_member_id', 'user_id', 'parameter_name', 'value', 'unit', 'record_date', 'record_time', 'notes']
        
        insert_fields = []
        values = []
        placeholders = []
        
        for field in fields:
            if field in data and data[field] is not None and data[field] != '':
                insert_fields.append(field)
                values.append(data[field])
                placeholders.append('?')
                
        query = f"INSERT INTO health_parameters ({', '.join(insert_fields)}) VALUES ({', '.join(placeholders)})"
        cursor = db.execute(query, values)
        db.commit()
        return cursor.lastrowid
        
    @staticmethod
    def delete(param_id, user_id):
        db = get_db()
        db.execute('DELETE FROM health_parameters WHERE id = ? AND user_id = ?', (param_id, user_id))
        db.commit()
        return True
        
    @staticmethod
    def get_trends(user_id, member_id, parameter, days=90):
        db = get_db()
        days_val = int(days) if days else 90
        return db.execute('''
            SELECT record_date, value, unit 
            FROM health_parameters 
            WHERE user_id = ? AND family_member_id = ? AND LOWER(parameter_name) = LOWER(?) AND record_date >= date('now', ?)
            ORDER BY record_date ASC, record_time ASC
        ''', (user_id, member_id, parameter, f'-{days_val} days')).fetchall()
        
    @staticmethod
    def get_latest(user_id, member_id=None):
        db = get_db()
        query = '''
            SELECT h1.* FROM health_parameters h1
            INNER JOIN (
                SELECT parameter_name, family_member_id, MAX(record_date) as max_date 
                FROM health_parameters 
                WHERE user_id = ?
        '''
        values = [user_id]
        
        if member_id:
            query += " AND family_member_id = ?"
            values.append(member_id)
            
        query += '''
                GROUP BY parameter_name, family_member_id
            ) h2 ON h1.parameter_name = h2.parameter_name 
            AND h1.family_member_id = h2.family_member_id 
            AND h1.record_date = h2.max_date
            WHERE h1.user_id = ?
        '''
        values.append(user_id)
        
        return db.execute(query, values).fetchall()
