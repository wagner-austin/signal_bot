#!/usr/bin/env python
"""
db/schema.py --- Database schema initialization for volunteer tables only.
Creates Volunteers, DeletedVolunteers, UserStates, then runs migrations.
Focuses on modular, unified, consistent code that facilitates future updates.
"""

from .connection import db_connection
from .migrations import run_migrations

def init_db() -> None:
    """
    init_db - Initialize the database by creating necessary base tables if they do not exist,
    then run any pending migrations to update the schema.
    """
    with db_connection() as conn:
        cursor = conn.cursor()

        # Volunteers table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Volunteers (
            phone TEXT PRIMARY KEY,
            name TEXT,
            skills TEXT,
            available INTEGER,
            role TEXT NOT NULL DEFAULT 'registered'
        )
        """)

        # DeletedVolunteers table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS DeletedVolunteers (
            phone TEXT PRIMARY KEY,
            name TEXT,
            skills TEXT,
            available INTEGER,
            role TEXT NOT NULL DEFAULT 'registered',
            deleted_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # UserStates table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserStates (
            phone TEXT PRIMARY KEY,
            flow_state TEXT DEFAULT '{}'
        )
        """)

        conn.commit()

    # Run migrations to keep volunteer schema up to date
    run_migrations()

# End of db/schema.py