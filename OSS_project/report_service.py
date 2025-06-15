from flask import request, redirect, url_for, render_template, session
from db import get_db
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            return "접근 권한이 없습니다.", 403
        return f(*args, **kwargs)
    return decorated

class ReportService:
    @admin_required
    def view_reports(self):
        db = get_db()
        reports = db.execute("""
            SELECT reports.id, reports.reason, reports.detail, reports.created_at,
                   posts.title AS post_title, posts.id AS post_id,
                   users.username
            FROM reports
            JOIN posts ON reports.post_id = posts.id
            JOIN users ON posts.user_id = users.id
            ORDER BY reports.created_at DESC
        """).fetchall()
        return render_template('report.html', reports=reports)

    def write_report(self):
        db = get_db()
        if request.method == 'POST':
            post_id = request.form.get('post_id')
            reasons = request.form.getlist('reason')
            detail = request.form.get('detail')
            reason_text = ", ".join(reasons)

            db.execute(
                "INSERT INTO reports (post_id, reason, detail) VALUES (?, ?, ?)",
                (post_id, reason_text, detail)
            )
            db.commit()

            post = db.execute("SELECT region_id FROM posts WHERE id = ?", (post_id,)).fetchone()
            return redirect(url_for('region', region_id=post['region_id']))

        post_id = request.args.get('post_id')
        return render_template('writeReport.html', post_id=post_id)

    def delete_report(self, report_id):
        db = get_db()
        db.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        db.commit()
        return redirect(url_for('report'))

    @admin_required
    def delete_and_warn(self, report_id):
        db = get_db()
        report = db.execute("SELECT post_id FROM reports WHERE id = ?", (report_id,)).fetchone()
        if not report:
            return "신고 정보를 찾을 수 없습니다.", 404

        post = db.execute("SELECT user_id, region_id FROM posts WHERE id = ?", (report['post_id'],)).fetchone()
        if not post:
            return "게시글이 존재하지 않습니다.", 404

        db.execute("DELETE FROM posts WHERE id = ?", (report['post_id'],))
        db.execute("UPDATE users SET warning_count = warning_count + 1 WHERE id = ?", (post['user_id'],))
        db.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        db.commit()

        return redirect(url_for('report'))
