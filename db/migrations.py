#!/usr/bin/env python
"""
db/migrations.py --- Database migrations management.
Provides a simple migration framework to automatically update the database schema.
Tracks the current schema version in a dedicated SchemaVersion table and applies new migrations as needed.
Now includes logic to skip migrations if the existing DB version is newer than our known migrations,
to avoid unintended downgrades.
"""

import logging
from .repository import execute_sql
from .connection import db_connection

logger = logging.getLogger(__name__)

def get_current_version() -> int:
    """
    get_current_version - Retrieve the current schema version from the SchemaVersion table.
    If the table does not exist, create it and initialize with version 0.
    
    Returns:
        int: The current schema version.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='SchemaVersion'")
        if not cursor.fetchone():
            cursor.execute("CREATE TABLE SchemaVersion (version INTEGER)")
            cursor.execute("INSERT INTO SchemaVersion (version) VALUES (0)")
            conn.commit()
            return 0
        else:
            row = cursor.execute("SELECT version FROM SchemaVersion").fetchone()
            return row["version"] if row else 0

def update_version(new_version: int) -> None:
    """
    update_version - Update the schema version in the SchemaVersion table.
    
    Args:
        new_version (int): The new schema version to set.
    """
    # Ensure the SchemaVersion table is present (and possibly initialized).
    _ = get_current_version()
    query = "UPDATE SchemaVersion SET version = ?"
    execute_sql(query, (new_version,), commit=True)

def migration_1() -> None:
    """
    Migration 1: Create Events and EventSpeakers tables.
    """
    execute_sql("""
    CREATE TABLE IF NOT EXISTS Events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        date TEXT,
        time TEXT,
        location TEXT,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """, commit=True)
    execute_sql("""
    CREATE TABLE IF NOT EXISTS EventSpeakers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER,
        speaker_name TEXT,
        speaker_topic TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(event_id) REFERENCES Events(event_id) ON DELETE CASCADE
    )
    """, commit=True)

def migration_2() -> None:
    """
    Migration 2: Create Resources table for storing resource links.
    """
    execute_sql("""
    CREATE TABLE IF NOT EXISTS Resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        title TEXT,
        url TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """, commit=True)

def migration_3() -> None:
    """
    migration_3 - Add preferred_role column to Volunteers table for volunteer role management.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(Volunteers)")
        columns = [row["name"] for row in cursor.fetchall()]
        if "preferred_role" not in columns:
            cursor.execute("ALTER TABLE Volunteers ADD COLUMN preferred_role TEXT")
            conn.commit()

def migration_4() -> None:
    """
    migration_4 - Create Tasks table for managing shared to-do items.
    """
    execute_sql("""
    CREATE TABLE IF NOT EXISTS Tasks (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT,
        created_by TEXT,
        assigned_to TEXT,
        status TEXT DEFAULT 'open',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """, commit=True)

def migration_5() -> None:
    """
    migration_5 - Create Donations table for donation tracking.
    """
    execute_sql("""
    CREATE TABLE IF NOT EXISTS Donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT,
        amount REAL,
        donation_type TEXT,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """, commit=True)

def migration_6() -> None:
    """
    migration_6 - Add preferred_role column to DeletedVolunteers table for volunteer role management.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(DeletedVolunteers)")
        columns = [row["name"] for row in cursor.fetchall()]
        if "preferred_role" not in columns:
            cursor.execute("ALTER TABLE DeletedVolunteers ADD COLUMN preferred_role TEXT")
            conn.commit()

def migration_7() -> None:
    """
    migration_7 - Extend UserStates table to support multi-step flows.
    Adds a new 'flow_state' column if not already present, and migrates existing 'has_seen_start' data.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(UserStates)")
        columns = [row["name"] for row in cursor.fetchall()]
        if "flow_state" not in columns:
            cursor.execute("ALTER TABLE UserStates ADD COLUMN flow_state TEXT DEFAULT '{}'")
            # Migrate existing has_seen_start values if present.
            if "has_seen_start" in columns:
                cursor.execute("UPDATE UserStates SET flow_state = '{\"has_seen_start\": true}' WHERE has_seen_start = 1")
                cursor.execute("UPDATE UserStates SET flow_state = '{\"has_seen_start\": false}' WHERE has_seen_start = 0")
        conn.commit()

# List of migrations: each tuple is (migration_version, migration_function)
MIGRATIONS = [
    (1, migration_1),
    (2, migration_2),
    (3, migration_3),
    (4, migration_4),
    (5, migration_5),
    (6, migration_6),
    (7, migration_7),
]

def run_migrations() -> None:
    """
    run_migrations - Run all pending migrations based on the current schema version.
    If the current version is newer than the highest known version in MIGRATIONS,
    we log a warning and skip to avoid unintended downgrades.
    """
    current_version = get_current_version()
    max_version = max(version for version, _ in MIGRATIONS)

    # If DB is already at a version higher than we know, skip migrations to avoid downgrade.
    if current_version > max_version:
        logger.warning(
            f"Detected DB schema version {current_version} which is newer than the code's "
            f"max known migration ({max_version}). Skipping migrations to prevent downgrade."
        )
        return

    for version, migration in MIGRATIONS:
        if version > current_version:
            migration()
            update_version(version)

# End of db/migrations.py