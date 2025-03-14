#!/usr/bin/env python
"""
tests/plugins/test_dbbackup_command.py - Tests for dbbackup command plugin.
Verifies subcommands: create, list, and restore, including invalid restore and subcommand scenarios.
"""

import os
import shutil
import pytest
from plugins.commands.dbbackup import dbbackup_command
from db.backup import BACKUP_DIR, list_backups, create_backup
from core.plugin_usage import USAGE_DBBACKUP

@pytest.fixture(autouse=True)
def cleanup_backups_dir():
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)
    yield
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)

def test_dbbackup_create():
    response = dbbackup_command("create", "+dummy", None, msg_timestamp=123)
    assert "Backup created:" in response
    backups = list_backups()
    assert len(backups) == 1

def test_dbbackup_list():
    create_backup()
    response = dbbackup_command("list", "+dummy", None, msg_timestamp=123)
    assert "Available Backups:" in response
    assert ".db" in response

def test_dbbackup_restore():
    create_backup()
    backups = list_backups()
    backup_filename = backups[-1]
    response = dbbackup_command(f"restore {backup_filename}", "+dummy", None, msg_timestamp=123)
    assert "Database restored from backup:" in response

def test_dbbackup_restore_invalid():
    response = dbbackup_command("restore nosuchfile.db", "+dummy", None, msg_timestamp=123)
    assert "Backup file 'nosuchfile.db' not found." in response

def test_dbbackup_invalid_subcommand():
    response = dbbackup_command("something_invalid", "+dummy", None, msg_timestamp=123)
    # Expect usage message from USAGE_DBBACKUP
    from core.plugin_usage import USAGE_DBBACKUP
    assert USAGE_DBBACKUP in response

# End of tests/plugins/test_dbbackup_command.py