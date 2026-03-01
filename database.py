import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "server.db")

db = sqlite3.connect(DB_PATH, check_same_thread=False)
sql = db.cursor()

# Users jadvali
sql.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(250),
    username VARCHAR(250),
    telegram_id BIGINT UNIQUE,
    status BOOLEAN DEFAULT 0,
    phone_number VARCHAR(20)
)""")

# Admins jadvali
sql.execute("""CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(250),
    username VARCHAR(250),
    telegram_id BIGINT UNIQUE,
    status BOOLEAN DEFAULT 0
)""")

db.commit()
