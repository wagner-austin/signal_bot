"""
core/database/schema.py - Database schema initialization.
Creates tables for volunteers, command logs, and deleted volunteers using a context manager for connection handling.
"""

from .connection import db_connection

def init_db() -> None:
    """
    Initialize the database by creating necessary tables if they do not exist.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Volunteers (
            phone TEXT PRIMARY KEY,
            name TEXT,
            skills TEXT,
            available INTEGER,
            current_role TEXT
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS CommandLogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            command TEXT,
            args TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS DeletedVolunteers (
            phone TEXT PRIMARY KEY,
            name TEXT,
            skills TEXT,
            available INTEGER,
            current_role TEXT,
            deleted_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()

# End of core/database/schema.py