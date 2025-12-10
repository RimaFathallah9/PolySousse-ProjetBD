import mysql.connector
from flask import g

#Configuration
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'smart_club',
}

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(**DB_CONFIG)
        g.db.row_factory = mysql.connector.cursor.MySQLCursorDict
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
