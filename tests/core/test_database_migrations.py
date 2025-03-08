#!/usr/bin/env python
"""
tests/core/test_database_migrations.py - Tests for database migrations.
Verifies that running migrations creates the necessary tables, updates the schema version,
and ensures that the DeletedVolunteers table has the new preferred_role column.
"""

import os
import sqlite3
import pytest
from core.database.migrations import get_current_version, run_migrations, MIGRATIONS, update_version
from core.database.connection import get_connection

@pytest.fixture(autouse=True)
def reset_schema(monkeypatch):
    """
    Reset the SchemaVersion table before each test by removing it if exists.
    This fixture ensures tests start from a known state.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS SchemaVersion")
    conn.commit()
    conn.close()
    yield

def test_get_current_version_initial():
    # Since SchemaVersion table was dropped, get_current_version should create it and return 0.
    version = get_current_version()
    assert version == 0

def test_run_migrations_creates_tables_and_updates_version():
    # Run migrations; this should create tables from all migrations.
    run_migrations()
    # After running migrations, schema version should equal the highest migration version.
    expected_version = max(version for version, _ in MIGRATIONS)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM SchemaVersion")
    row = cursor.fetchone()
    conn.close()
    assert row is not None
    assert row["version"] == expected_version

    # Check that tables from migrations exist.
    conn = get_connection()
    cursor = conn.cursor()
    expected_tables = {"Events", "EventSpeakers", "Resources", "Tasks", "Donations"}
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = set(row["name"] for row in cursor.fetchall())
    conn.close()
    # Some tables (like Volunteers, CommandLogs, DeletedVolunteers, SchemaVersion) may also exist.
    for table in expected_tables:
        assert table in tables

def test_deleted_volunteers_has_preferred_role_column():
    """
    Test that the DeletedVolunteers table has a 'preferred_role' column after migrations.
    """
    run_migrations()  # Ensure migrations are applied
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(DeletedVolunteers)")
    columns = [row["name"] for row in cursor.fetchall()]
    conn.close()
    assert "preferred_role" in columns, "DeletedVolunteers table should have a 'preferred_role' column."

# End of tests/core/test_database_migrations.py