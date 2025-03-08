#!/usr/bin/env python
"""
tests/conftest.py - Pytest configuration, fixtures, and common setup.
Overrides DB_NAME for test isolation and provides a fixture to clear key database tables.
Ensures that Volunteers, DeletedVolunteers, Resources, Events, EventSpeakers, Tasks, and Donations tables are emptied before and after tests.
"""

import os
import tempfile
import pytest

# Immediately override DB_NAME for tests before any other modules are imported.
fd, temp_db_path = tempfile.mkstemp(prefix="bot_data_test_", suffix=".db")
os.close(fd)
os.environ["DB_NAME"] = temp_db_path

@pytest.fixture(scope="session", autouse=True)
def test_database():
    """
    tests/conftest.py – Creates and initializes a temporary database for testing.
    The DB_NAME environment variable is set to a temporary file for isolation.
    After tests, the temporary database file is removed and DB_NAME is unset.
    """
    import core.database as db
    db.init_db()
    yield
    try:
        os.remove(temp_db_path)
    except Exception:
        pass
    os.environ.pop("DB_NAME", None)

@pytest.fixture(autouse=True)
def clear_database_tables():
    """
    tests/conftest.py – Fixture to clear key tables (Volunteers, DeletedVolunteers, Resources,
    Events, EventSpeakers, Tasks, and Donations) before and after tests.
    Ensures a clean database state to prevent data leakage between tests.
    """
    from core.database.connection import get_connection
    def clear_tables():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Volunteers")
        cursor.execute("DELETE FROM DeletedVolunteers")
        cursor.execute("DELETE FROM Resources")
        cursor.execute("DELETE FROM Events")
        cursor.execute("DELETE FROM EventSpeakers")
        cursor.execute("DELETE FROM Tasks")
        cursor.execute("DELETE FROM Donations")
        conn.commit()
        conn.close()
    clear_tables()
    yield
    clear_tables()

# End of tests/conftest.py