import sqlite3
import uuid
import sys
from config import DB_FILE

def init_db():
    """Initializes the database and creates the thread_names table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # This table will map user-given names to unique session_ids
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS thread_names (
                session_id TEXT PRIMARY KEY,
                thread_name TEXT NOT NULL
            );
        """)
        conn.commit()
        conn.close()
        print("Database initialized for thread names.")
        sys.stdout.flush()
    except Exception as e:
        print(f"Error initializing DB: {e}")
        sys.stdout.flush()

def get_threads() -> dict:
    """Fetches all existing threads as a dictionary of {session_id: thread_name}."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT session_id, thread_name FROM thread_names ORDER BY thread_name")
        threads = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return threads
    except Exception as e:
        print(f"Error getting threads: {e}")
        sys.stdout.flush()
        return {}

def create_thread(thread_name: str) -> str:
    """Creates a new thread with a given name, returns the new session_id."""
    try:
        session_id = str(uuid.uuid4())
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO thread_names (session_id, thread_name) VALUES (?, ?)", (session_id, thread_name))
        conn.commit()
        conn.close()
        print(f"Created new thread: {thread_name} (ID: {session_id})")
        sys.stdout.flush()
        return session_id
    except Exception as e:
        print(f"Error creating thread: {e}")
        sys.stdout.flush()
        return None