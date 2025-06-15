import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g, session
from functools import wraps
from board_service import BoardService
from db import get_db, close_db
from report_service import ReportService
from admin_service import AdminService
from access_service import AccessService
from region import Region

app = Flask(__name__)

@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

board_service = BoardService()
report_service = ReportService()
admin_service = AdminService()
access_service = AccessService()

app = Flask(__name__, template_folder="templates")
app.secret_key = 'your_secret_key_here'
DATABASE = os.path.join(app.root_path, 'instance', 'users.db')

# DB 초기화 함수
def init_db():
    with app.app_context():
        db = get_db()
        with open(os.path.join(app.root_path, 'schema.sql'), encoding='utf-8') as f:
            db.executescript(f.read())

        # 기본 관리자 계정
        admin = db.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
        if not admin:
            db.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ('admin', 'admin', 'admin')
            )
        db.commit()


# 메인 화면(초기 화면)
@app.route('/')
def main():
    return render_template('main.html')

# 회원가입
app.add_url_rule(
    '/register',
    view_func=access_service.register,
    methods=['GET', 'POST'],
    endpoint='register'
)


# 로그인
app.add_url_rule(
    '/login',
    view_func=access_service.login,
    methods=['GET', 'POST'],
    endpoint='login'
)

# 로그아웃
app.add_url_rule(
    '/logout',
    view_func=access_service.logout,
    endpoint='logout'
)


# 지역 선택 및 게시판 목록
@app.route('/search')
def select():
    return render_template('search.html')


# 지역 게시판
@app.route('/region/<int:region_id>', endpoint='region')
def region(region_id):
    db = get_db()
    posts = db.execute(
        "SELECT posts.*, users.username AS author FROM posts JOIN users ON posts.user_id = users.id WHERE region_id = ? ORDER BY created_at DESC",
        (region_id,)).fetchall()

    region_obj = Region.get_by_id(region_id)
    region_name = region_obj["name"] if region_obj else "Unknown Region"

    return render_template('board.html', region=region_name, posts=posts, region_id=region_id)


# 글 작성
app.add_url_rule(
    '/write/<int:region_id>',
    view_func=board_service.write_post,
    methods=['GET', 'POST'],
    endpoint='write'
)

# 글 수정
app.add_url_rule(
    '/edit/<int:post_id>',
    view_func=board_service.edit_post,
    methods=['GET', 'POST'],
    endpoint='edit'
)

# 글 삭제
app.add_url_rule(
    '/delete/<int:post_id>',
    view_func=board_service.delete_post,
    methods=['POST'],
    endpoint='delete'
)


# 신고 글 관리 화면
app.add_url_rule(
    '/report',
    view_func=report_service.view_reports,
    endpoint='report'
)


# 신고 글 삭제
app.add_url_rule(
    '/deleteReport/<int:report_id>',
    view_func=report_service.delete_report,
    methods=['POST'],
    endpoint='delete_report'
)


# 신고 글 작성
app.add_url_rule(
    '/writeReport',
    view_func=report_service.write_report,
    methods=['GET', 'POST'],
    endpoint='writeReport'
)

# 사용자 신고 관리
app.add_url_rule(
    '/deleteAndWarn/<int:report_id>',
    view_func=report_service.delete_and_warn,
    methods=['POST'],
    endpoint='delete_and_warn'
)

# 사용자 관리 화면
app.add_url_rule(
    '/manageUser',
    view_func=admin_service.manage_users,
    endpoint='manageUser'
)

# 사용자 경고 추가
app.add_url_rule(
    '/warn/<int:user_id>',
    view_func=admin_service.warn_user,
    methods=['POST'],
    endpoint='warn_user'
)


# 사용자 경고 취소
app.add_url_rule(
    '/unwarn/<int:user_id>',
    view_func=admin_service.unwarn_user,
    methods=['POST'],
    endpoint='unwarn_user'
)


# 생성자 (DB 초기화)
if __name__ == '__main__':
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)
