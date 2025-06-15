from flask import render_template, request, redirect, url_for, session
from db import get_db
from region import Region


class BoardService:
    def write_post(self, region_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        db = get_db()
        region = Region.get_by_id(region_id)  # 지역 정보 가져오기

        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            user_id = session['user_id']

            db.execute(
                "INSERT INTO posts (user_id, region_id, title, content) VALUES (?, ?, ?, ?)",
                (user_id, region_id, title, content)
            )
            db.commit()
            return redirect(url_for('region', region_id=region_id))

        return render_template('write.html', region=region, region_id=region_id)

    def edit_post(self, post_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        db = get_db()
        post = db.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        if post['user_id'] != session['user_id'] and session.get('role') != 'admin':
            return "권한이 없습니다.", 403

        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            db.execute("UPDATE posts SET title = ?, content = ? WHERE id = ?",
                       (title, content, post_id))
            db.commit()
            return redirect(url_for('region', region_id=post['region_id']))

        return render_template('edit.html', post=post)

    def delete_post(self, post_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        db = get_db()
        post = db.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        if post['user_id'] != session['user_id'] and session.get('role') != 'admin':
            return "권한이 없습니다.", 403

        region_id = post['region_id']
        db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        db.commit()
        return redirect(url_for('region', region_id=region_id))
