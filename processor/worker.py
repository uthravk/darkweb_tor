# processor/worker.py
import sqlite3, time, json
from datetime import datetime
from processor.nlp_pipeline import analyze_text
from utils.storage import db_path

def get_next_unprocessed():
    conn = sqlite3.connect(db_path())
    c = conn.cursor()
    c.execute("SELECT id, text FROM posts WHERE processed=0 ORDER BY id ASC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row

def mark_processed(post_id):
    conn = sqlite3.connect(db_path())
    c = conn.cursor()
    c.execute("UPDATE posts SET processed=1 WHERE id=?", (post_id,))
    conn.commit()
    conn.close()

def insert_alert(post_id, score, labels):
    conn = sqlite3.connect(db_path())
    c = conn.cursor()
    c.execute("INSERT INTO alerts (post_id, score, labels, created_at) VALUES (?, ?, ?, ?)",
              (post_id, score, json.dumps(labels), datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def main_loop():
    print("Worker started...")
    while True:
        row = get_next_unprocessed()
        if not row:
            time.sleep(2)
            continue
        post_id, text = row
        print("Processing", post_id)
        score, labels = analyze_text(text)
        print("Score", score, "Labels", labels)
        if score >= 0.4:
            insert_alert(post_id, score, labels)
        mark_processed(post_id)
        time.sleep(0.5)

if __name__ == "__main__":
    main_loop()
