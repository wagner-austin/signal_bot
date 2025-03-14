"""
tests/core/test_database_schema.py - Tests for the database schema module.
Verifies that init_db creates the necessary tables.
"""

from db.schema import init_db
from db.connection import get_connection

def test_init_db_creates_tables():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    # Check for the Volunteers table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Volunteers'")
    assert cursor.fetchone() is not None
    # Check for the CommandLogs table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='CommandLogs'")
    assert cursor.fetchone() is not None
    # Check for the DeletedVolunteers table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='DeletedVolunteers'")
    assert cursor.fetchone() is not None
    conn.close()

# End of tests/core/test_database_schema.py