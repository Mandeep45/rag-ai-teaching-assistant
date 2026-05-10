import sqlite3
import json
from datetime import datetime

def get_db():
    conn = sqlite3.connect("chat_history.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized!")

def save_message(session_id, question, answer, sources):
    conn = get_db()
    conn.execute("""
        INSERT INTO conversations (session_id, question, answer, sources)
        VALUES (?, ?, ?, ?)
    """, (session_id, question, answer, json.dumps(sources)))
    conn.commit()
    conn.close()

def get_history(session_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT question, answer, sources, timestamp
        FROM conversations
        WHERE session_id = ?
        ORDER BY timestamp ASC
    """, (session_id,)).fetchall()
    conn.close()
    return [{"question": r["question"], "answer": r["answer"], "sources": json.loads(r["sources"]), "timestamp": r["timestamp"]} for r in rows]

def get_all_sessions():
    conn = get_db()
    rows = conn.execute("""
        SELECT session_id, 
               MIN(timestamp) as started, 
               COUNT(*) as total_messages,
               MIN(question) as first_question
        FROM conversations
        GROUP BY session_id
        ORDER BY started DESC
    """).fetchall()
    conn.close()
    return [{"session_id": r["session_id"], "started": r["started"], "total_messages": r["total_messages"], "first_question": r["first_question"]} for r in rows]