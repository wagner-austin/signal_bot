"""
tests/core/test_database_helpers.py – Tests for database helper functions.
Ensures that execute_sql correctly returns fetchone and fetchall results.
"""

import sqlite3
import pytest
from db.connection import db_connection
from db.repository import execute_sql

def test_execute_sql_fetchone():
    # Create a temporary table and insert a record.
    with db_connection() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS TestTable (id INTEGER PRIMARY KEY, value TEXT)")
        conn.execute("INSERT INTO TestTable (value) VALUES (?)", ("test_value",))
        conn.commit()
    result = execute_sql("SELECT value FROM TestTable WHERE id = ?", (1,), fetchone=True)
    assert result is not None
    assert result["value"] == "test_value"

def test_execute_sql_fetchall():
    with db_connection() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS TestTable (id INTEGER PRIMARY KEY, value TEXT)")
        conn.execute("DELETE FROM TestTable")  # Clear table
        conn.executemany("INSERT INTO TestTable (value) VALUES (?)", [("val1",), ("val2",), ("val3",)])
        conn.commit()
    results = execute_sql("SELECT value FROM TestTable", fetchall=True)
    assert len(results) == 3
    values = [row["value"] for row in results]
    assert "val1" in values and "val2" in values and "val3" in values

# End of tests/core/test_database_helpers.py