
-- 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    warning_count INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1
);

-- 게시글 테이블
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    region_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- 신고
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    detail TEXT,
    created_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(post_id) REFERENCES posts(id)
);

-- 신고 조회
SELECT reports.id, reports.reason, reports.detail, reports.created_at,
       posts.title, posts.id AS post_id, users.username
FROM reports
JOIN posts ON reports.post_id = posts.id
JOIN users ON posts.user_id = users.id
ORDER BY reports.created_at DESC;