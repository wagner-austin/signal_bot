#!/usr/bin/env python
"""
db/migrations.py --- Database migrations management for volunteer flows only.
Now only includes:
  1) Migration to add 'preferred_role' to DeletedVolunteers
  2) Migration to extend UserStates table with 'flow_state'
"""

import logging
from .repository import execute_sql
from .connection import db_connection

logger = logging.getLogger(__name__)

def get_current_version() -> int:
    """
    Retrieve the current schema version from the SchemaVersion table.
    If the table does not exist, create it and initialize with version 0.
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
    Update the schema version in the SchemaVersion table.
    """
    _ = get_current_version()  # Ensure table is there
    query = "UPDATE SchemaVersion SET version = ?"
    execute_sql(query, (new_version,), commit=True)

# --------------------------
# Volunteer-Related Migrations
# --------------------------

def migration_1():
    """
    migration_1 - Add 'preferred_role' column to DeletedVolunteers (originally old migration_2).
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(DeletedVolunteers)")
        columns = [row["name"] for row in cursor.fetchall()]
        if "preferred_role" not in columns:
            cursor.execute("ALTER TABLE DeletedVolunteers ADD COLUMN preferred_role TEXT")
            conn.commit()

def migration_2():
    """
    migration_2 - Extend UserStates table to support multi-step flows (originally old migration_3).
    Adds a new 'flow_state' column if not already present.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(UserStates)")
        columns = [row["name"] for row in cursor.fetchall()]
        if "flow_state" not in columns:
            cursor.execute("ALTER TABLE UserStates ADD COLUMN flow_state TEXT DEFAULT '{}'")
            conn.commit()

MIGRATIONS = [
    (1, migration_1),
    (2, migration_2)
]

def run_migrations() -> None:
    """
    Run all pending migrations based on the current schema version.
    """
    current_version = get_current_version()
    max_version = max(version for version, _ in MIGRATIONS)

    if current_version > max_version:
        logger.warning(
            f"Detected DB schema version {current_version} newer than known migrations. "
            f"Skipping migrations to prevent downgrade."
        )
        return

    for version, migration_fn in MIGRATIONS:
        if version > current_version:
            migration_fn()
            update_version(version)

# End of db/migrations.py