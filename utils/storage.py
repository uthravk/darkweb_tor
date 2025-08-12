# utils/storage.py
import os, sqlite3
from dotenv import load_dotenv
load_dotenv()

DB = os.getenv("SQLITE_PATH", "./data/darkweb.db")

def db_path():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    return DB

def init_db():
    conn = sqlite3.connect(db_path())
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        url TEXT,
        title TEXT,
        text TEXT,
        timestamp TEXT,
        metadata TEXT,
        processed INTEGER DEFAULT 0
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        score REAL,
        labels TEXT,
        created_at TEXT
    )""")
    conn.commit()
    conn.close()
