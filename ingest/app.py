# ingest/app.py
import os, sqlite3, json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from utils.storage import init_db, db_path

# initialize DB
init_db()

app = FastAPI(title="DarkWeb Intel Ingest API")

class IngestItem(BaseModel):
    source: str
    url: str = None
    title: str = None
    text: str
    timestamp: str = None
    metadata: dict = {}

@app.post("/ingest", status_code=201)
def ingest(item: IngestItem):
    ts = item.timestamp or datetime.utcnow().isoformat()
    conn = sqlite3.connect(db_path())
    c = conn.cursor()
    c.execute(
        "INSERT INTO posts (source, url, title, text, timestamp, metadata, processed) VALUES (?, ?, ?, ?, ?, ?, 0)",
        (item.source, item.url, item.title, item.text, ts, json.dumps(item.metadata))
    )
    conn.commit()
    post_id = c.lastrowid
    conn.close()
    return {"post_id": post_id}

@app.get("/posts/{post_id}")
def get_post(post_id: int):
    conn = sqlite3.connect(db_path())
    c = conn.cursor()
    c.execute("SELECT id, source, url, title, text, timestamp, metadata, processed FROM posts WHERE id=?", (post_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "id": row[0],
        "source": row[1],
        "url": row[2],
        "title": row[3],
        "text": row[4],
        "timestamp": row[5],
        "metadata": json.loads(row[6]) if row[6] else {},
        "processed": bool(row[7])
    }

@app.get("/alerts")
def list_alerts(limit: int = 50):
    conn = sqlite3.connect(db_path())
    c = conn.cursor()
    c.execute("SELECT id, post_id, score, labels, created_at FROM alerts ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    out = []
    for r in rows:
        out.append({"id": r[0], "post_id": r[1], "score": r[2], "labels": json.loads(r[3]), "created_at": r[4]})
    return out

