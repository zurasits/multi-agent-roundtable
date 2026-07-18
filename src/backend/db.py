import sqlite3
import os
from dataclasses import dataclass
from typing import List

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../roundtable.db")

@dataclass
class Agent:
    id: str
    name: str
    role: str
    llm_provider: str = "gemini"

@dataclass
class Message:
    id: str
    session_id: str
    agent_id: str
    content: str
    timestamp: str

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            llm_provider TEXT DEFAULT 'gemini'
        )
    """)
    # Auto-migrate: Add column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE agents ADD COLUMN llm_provider TEXT DEFAULT 'gemini'")
    except sqlite3.OperationalError:
        pass
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    
    # Insert default agents if not present
    cursor.execute("SELECT COUNT(*) FROM agents")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO agents (id, name, role) VALUES (?, ?, ?)
        """, [
            ("agent_1", "Alice", "Analyst"),
            ("agent_2", "Bob", "Reviewer")
        ])
    conn.commit()
    conn.close()

def get_all_agents() -> List[Agent]:
    conn = get_db_connection()
    cursor = conn.cursor()
    # Using 'SELECT *' or explicitly selecting columns
    cursor.execute("SELECT id, name, role, llm_provider FROM agents")
    rows = cursor.fetchall()
    conn.close()
    # row.keys() might not exist for row_factory = sqlite3.Row in all environments but dict(row).get() works
    return [Agent(id=row["id"], name=row["name"], role=row["role"], llm_provider=dict(row).get("llm_provider", "gemini")) for row in rows]

def update_agent_provider(agent_id: str, provider: str) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE agents SET llm_provider = ? WHERE id = ?", (provider, agent_id))
    conn.commit()
    conn.close()

def get_session_messages(session_id: str) -> List[Message]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, session_id, agent_id, content, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        Message(
            id=row["id"],
            session_id=row["session_id"],
            agent_id=row["agent_id"],
            content=row["content"],
            timestamp=row["timestamp"]
        ) for row in rows
    ]

def add_message(msg: Message) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (id, session_id, agent_id, content, timestamp) VALUES (?, ?, ?, ?, ?)",
        (msg.id, msg.session_id, msg.agent_id, msg.content, msg.timestamp)
    )
    conn.commit()
    conn.close()

# Auto-initialize the database on import
init_db()
