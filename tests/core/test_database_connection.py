"""
tests/core/test_database_connection.py - Tests for the database connection module.
Verifies that get_connection returns a valid SQLite connection.
"""

import sqlite3
from core.database.connection import get_connection

def test_get_connection():
    conn = get_connection()
    assert isinstance(conn, sqlite3.Connection)
    # Check that the row_factory is set to sqlite3.Row
    assert conn.row_factory == sqlite3.Row
    conn.close()

# End of test/core/test_database_connection.py