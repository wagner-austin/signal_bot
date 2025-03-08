"""
tests/conftest.py – Pytest configuration, fixtures, and common setup.
Overrides DB_NAME for test isolation and provides a clear_volunteers fixture.
Also clears Resources table for test isolation.
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
def clear_volunteers():
    """
    tests/conftest.py – Fixture to clear Volunteers, DeletedVolunteers, and Resources tables before and after tests.
    """
    from core.database.connection import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Volunteers")
    cursor.execute("DELETE FROM DeletedVolunteers")
    cursor.execute("DELETE FROM Resources")
    conn.commit()
    conn.close()
    yield
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Volunteers")
    cursor.execute("DELETE FROM DeletedVolunteers")
    cursor.execute("DELETE FROM Resources")
    conn.commit()
    conn.close()

# End of tests/conftest.py