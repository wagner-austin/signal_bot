#!/usr/bin/env python
"""
test_database_backup.py - Tests for database backup and restore functionality.
Verifies that backups are created, listed, cleaned up per retention policy, and that restore functionality works.
Also tests error handling for backup directory creation (mocking os.makedirs to raise OSError).
"""

import os
import shutil
import sqlite3
import pytest
from unittest.mock import patch
from core.database.backup import create_backup, list_backups, cleanup_backups, restore_backup, BACKUP_DIR
from core.database.connection import get_connection
from core.config import DB_NAME

def test_create_backup():
    # Ensure no backups initially
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)
    try:
        backup_path = create_backup()
        # The creation may return an empty string if it failed
        assert backup_path != "", "Expected a valid backup path string."
        assert os.path.exists(backup_path)
        backups = list_backups()
        assert len(backups) == 1
    finally:
        if os.path.exists(BACKUP_DIR):
            shutil.rmtree(BACKUP_DIR)

def test_cleanup_backups():
    try:
        # Create 12 dummy backup files manually
        if os.path.exists(BACKUP_DIR):
            shutil.rmtree(BACKUP_DIR)
        os.makedirs(BACKUP_DIR)
        for i in range(12):
            filename = f"backup_20210101_00000{i}.db"
            filepath = os.path.join(BACKUP_DIR, filename)
            with open(filepath, "w") as f:
                f.write("dummy")
        cleanup_backups(max_backups=10)
        backups = list_backups()
        assert len(backups) == 10
        # Check that the oldest backup is removed
        assert "backup_20210101_000000.db" not in backups
    finally:
        if os.path.exists(BACKUP_DIR):
            shutil.rmtree(BACKUP_DIR)

def test_restore_backup():
    try:
        # Initialize a valid SQLite database with known content.
        conn = get_connection()
        cursor = conn.cursor()
        # Create a test table and insert a known row.
        cursor.execute("CREATE TABLE IF NOT EXISTS TestData (id INTEGER PRIMARY KEY, value TEXT)")
        cursor.execute("DELETE FROM TestData")  # Ensure clean table
        cursor.execute("INSERT INTO TestData (value) VALUES (?)", ("original",))
        conn.commit()
        conn.close()

        # Create a backup of the valid database.
        backup_path = create_backup()
        backup_filename = backup_path.split(os.sep)[-1]

        # Modify the database using SQL (update the row).
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE TestData SET value = ? WHERE id = 1", ("modified",))
        conn.commit()
        conn.close()

        # Verify that the data has been modified.
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM TestData WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        assert row is not None and row["value"] == "modified"

        # Restore the database from the backup.
        result = restore_backup(backup_filename)
        assert result is True

        # Verify that the data is reverted to the original state.
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM TestData WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        assert row is not None and row["value"] == "original"
    finally:
        if os.path.exists(BACKUP_DIR):
            shutil.rmtree(BACKUP_DIR)

@pytest.mark.parametrize("os_error", [OSError("Test OSError")])
def test_create_backup_makedirs_failure(os_error):
    """
    Test that when os.makedirs() fails with an OSError, create_backup() handles it gracefully.
    """
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)
    with patch("os.makedirs", side_effect=os_error):
        backup_path = create_backup()
        # Expect an empty string to signal the backup was skipped or failed gracefully.
        assert backup_path == "", "create_backup should return an empty string on directory creation failure."
    assert not os.path.exists(BACKUP_DIR), "Backup directory should not exist after a forced failure."

# End of tests/core/test_database_backup.py