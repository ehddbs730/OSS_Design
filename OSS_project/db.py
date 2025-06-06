# db.py
import sqlite3
import os
from flask import g, current_app

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db_path = os.path.join(current_app.root_path, 'instance', 'users.db')
        db = g._database = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
    return db

def close_db(e=None):
    db = g.pop('_database', None)
    if db is not None:
        db.close()
