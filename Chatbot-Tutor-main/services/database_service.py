# This is the database service responsible for storing responses 
# from interactions.
# Will store up to 25 responses, to avoid indefinite grow of db,
# and will reset.

import sqlite3
from datetime import datetime

DB_NAME = "chatbot_logs.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT,
            question TEXT,
            intent TEXT,
            answer TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def log_interaction(video_id, question, intent, answer):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Reset database
    cursor.execute("SELECT COUNT(*) FROM interactions")
    count = cursor.fetchone()[0]

    # When interaction count reaches 25 reset database table
    if count >= 25:
        cursor.execute("DELETE FROM interactions")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='interactions'")

    cursor.execute("""
        INSERT INTO interactions (video_id, question, intent, answer, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        video_id,
        question,
        intent,
        answer,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_recent_logs(limit=25):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, video_id, question, intent, answer, created_at
        FROM interactions
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]

    conn.close()

    logs = []

    for row in rows:
        logs.append(dict(zip(columns, row)))

    return logs