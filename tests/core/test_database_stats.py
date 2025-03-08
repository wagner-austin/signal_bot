#!/usr/bin/env python
"""
tests/core/test_database_stats.py - Tests for the database statistics module.
Verifies that get_database_stats returns row counts excluding unwanted tables and correctly reports the schema version.
"""

from core.database.stats import get_database_stats
from core.database.connection import get_connection

def test_get_database_stats_excludes_unwanted():
    stats = get_database_stats()
    # Unwanted tables should not appear
    for unwanted in ["sqlite_sequence", "SchemaVersion", "CommandLogs"]:
        assert unwanted not in stats["tables"]

def test_schema_version():
    stats = get_database_stats()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='SchemaVersion'")
    exists = cursor.fetchone() is not None
    conn.close()
    if exists:
        assert stats["schema_version"] is not None

# End of tests/core/test_database_stats.py