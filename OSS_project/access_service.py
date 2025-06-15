from flask import request, redirect, url_for, render_template, session
from db import get_db

class AccessService:
    def login(self):
        message = None
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            db = get_db()
            user = db.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password)
            ).fetchone()

            if user:
                if user['is_active'] == 0:
                    message = "이 계정은 정지되어 로그인할 수 없습니다."
                    return render_template('Login.html', message=message)
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                return redirect(url_for('select'))
            else:
                message = "아이디 또는 비밀번호가 올바르지 않습니다."

        return render_template('Login.html', message=message)

    def register(self):
        message = None
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if password != confirm_password:
                message = "비밀번호가 일치하지 않습니다."
            else:
                db = get_db()
                try:
                    db.execute(
                        "INSERT INTO users (username, password) VALUES (?, ?)",
                        (username, password)
                    )
                    db.commit()
                    return redirect(url_for('login'))
                except Exception:
                    message = "이미 존재하는 아이디입니다."

        return render_template('Register.html', message=message)

    def logout(self):
        session.clear()
        return redirect(url_for('main'))
