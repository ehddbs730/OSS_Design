# admin_service.py
from flask import render_template, redirect, url_for, session
from db import get_db
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            return "접근 권한이 없습니다.", 403
        return f(*args, **kwargs)
    return decorated

class AdminService:
    @admin_required
    def manage_users(self):
        db = get_db()
        users = db.execute(
            "SELECT id, username, role, warning_count, is_active FROM users ORDER BY id"
        ).fetchall()
        return render_template('manageUser.html', users=users)

    @admin_required
    def warn_user(self, user_id):
        db = get_db()
        db.execute("""
            UPDATE users 
            SET warning_count = warning_count + 1,
                is_active = CASE WHEN warning_count + 1 >= 3 THEN 0 ELSE is_active END
            WHERE id = ?
        """, (user_id,))
        db.commit()
        return redirect(url_for('manageUser'))

    @admin_required
    def unwarn_user(self, user_id):
        db = get_db()
        db.execute("""
            UPDATE users 
            SET warning_count = CASE 
                WHEN warning_count > 0 THEN warning_count - 1 
                ELSE 0 
            END 
            WHERE id = ?
        """, (user_id,))
        db.commit()
        return redirect(url_for('manageUser'))
