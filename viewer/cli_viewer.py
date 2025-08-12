# viewer/cli_viewer.py
import sqlite3
from utils.storage import db_path

def show_alerts(limit=50):
    conn = sqlite3.connect(db_path())
    c = conn.cursor()
    c.execute("SELECT a.id, a.score, a.labels, a.created_at, p.text FROM alerts a JOIN posts p ON a.post_id = p.id ORDER BY a.created_at DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    for r in rows:
        print("=== ALERT ID:", r[0], "SCORE:", r[1], "TIME:", r[3])
        print("LABELS:", r[2])
        print("SNIPPET:", (r[4] or "")[:400])
        print("----\n")

if __name__ == "__main__":
    show_alerts()

