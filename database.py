import psycopg2
import psycopg2.extras
import json
import os
from datetime import datetime

# Render PostgreSQL Internal Database URL
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            session_id TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources JSONB,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

    print("PostgreSQL database initialized!")

def save_message(session_id, question, answer, sources):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO conversations 
        (session_id, question, answer, sources)
        VALUES (%s, %s, %s, %s)
    """, (
        session_id,
        question,
        answer,
        json.dumps(sources)
    ))

    conn.commit()
    cur.close()
    conn.close()

def get_history(session_id):
    conn = get_db()

    cur = conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    cur.execute("""
        SELECT question, answer, sources, timestamp
        FROM conversations
        WHERE session_id = %s
        ORDER BY timestamp ASC
    """, (session_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "question": r["question"],
            "answer": r["answer"],
            "sources": r["sources"],
            "timestamp": str(r["timestamp"])
        }
        for r in rows
    ]

def get_all_sessions():
    conn = get_db()

    cur = conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    cur.execute("""
        SELECT 
            session_id,
            MIN(timestamp) as started,
            COUNT(*) as total_messages,
            MIN(question) as first_question
        FROM conversations
        GROUP BY session_id
        ORDER BY started DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "session_id": r["session_id"],
            "started": str(r["started"]),
            "total_messages": r["total_messages"],
            "first_question": r["first_question"]
        }
        for r in rows
    ]