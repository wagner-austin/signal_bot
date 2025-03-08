#!/usr/bin/env python
"""
tests/conftest.py - Consolidated test fixtures and common setup for database isolation, CLI simulation, and plugin registration.
This module overrides DB_NAME for test isolation, clears key database tables, and provides common fixtures including a unified CLI runner.
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
    tests/conftest.py - Creates and initializes a temporary database for testing.
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
    tests/conftest.py - Fixture to clear key tables (Volunteers, DeletedVolunteers, Resources,
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

@pytest.fixture
def dummy_plugin():
    """
    tests/conftest.py - Fixture for dummy plugin registration.
    Registers a dummy plugin in plugins.manager.plugin_registry and unregisters it after the test.
    """
    from plugins.manager import plugin_registry
    dummy_plugin_data = {
        "function": lambda args, sender, state_machine, msg_timestamp=None: "yes",
        "aliases": ["test"],
        "help_visible": True,
    }
    plugin_registry["test"] = dummy_plugin_data
    yield dummy_plugin_data
    plugin_registry.pop("test", None)

@pytest.fixture
def cli_runner():
    """
    tests/conftest.py - Fixture for CLI command simulation.
    Provides a unified helper to simulate CLI command invocations of cli_tools.py.
    """
    from tests.cli.cli_test_helpers import run_cli_command
    yield run_cli_command

# End of tests/conftest.py