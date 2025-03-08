"""
core/database/schema.py - Database schema initialization.
Creates base tables for volunteers, command logs, and deleted volunteers.
Automatically runs migrations to update the schema with new changes.
"""

from .connection import db_connection
from .migrations import run_migrations

def init_db() -> None:
    """
    Initialize the database by creating necessary base tables if they do not exist,
    then run any pending migrations to update the schema.
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
    # Run migrations to update or add new tables/columns as needed.
    run_migrations()

# End of core/database/schema.py