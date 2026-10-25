from models.db import get_db

class Notification:
    @staticmethod
    def get_all(user_id, is_read=None, limit=50):
        db = get_db()
        query = "SELECT * FROM notifications WHERE user_id = ?"
        values = [user_id]
        
        if is_read is not None:
            query += " AND is_read = ?"
            values.append(int(is_read))
            
        query += " ORDER BY created_at DESC LIMIT ?"
        values.append(limit)
        
        return db.execute(query, values).fetchall()
        
    @staticmethod
    def create(user_id, type, title, message, link=None):
        db = get_db()
        cursor = db.execute(
            'INSERT INTO notifications (user_id, type, title, message, link) VALUES (?, ?, ?, ?, ?)',
            (user_id, type, title, message, link)
        )
        db.commit()
        return cursor.lastrowid
        
    @staticmethod
    def mark_read(notification_id, user_id):
        db = get_db()
        db.execute('UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?', (notification_id, user_id))
        db.commit()
        return True
        
    @staticmethod
    def mark_all_read(user_id):
        db = get_db()
        db.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ? AND is_read = 0', (user_id,))
        db.commit()
        return True
        
    @staticmethod
    def delete(notification_id, user_id):
        db = get_db()
        db.execute('DELETE FROM notifications WHERE id = ? AND user_id = ?', (notification_id, user_id))
        db.commit()
        return True
        
    @staticmethod
    def get_unread_count(user_id):
        db = get_db()
        result = db.execute('SELECT COUNT(*) as count FROM notifications WHERE user_id = ? AND is_read = 0', (user_id,)).fetchone()
        return result['count'] if result else 0
