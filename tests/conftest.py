"""
tests/conftest.py - Pytest configuration and fixtures.
Provides a temporary database fixture to ensure tests run even if no database exists.
"""

import os
import shutil
import pytest

@pytest.fixture(scope="session", autouse=True)
def test_database(tmp_path_factory):
    """
    Creates a temporary database for testing.
    Sets the DB_NAME environment variable to point to a temporary file,
    calls init_db() to create necessary tables, and cleans up after tests.
    This allows tests to run even if no pre-existing database is present.
    """
    # Create a temporary directory for the test database.
    temp_dir = tmp_path_factory.mktemp("test_db")
    db_path = temp_dir / "bot_data_test.db"
    # Set the environment variable DB_NAME to this temporary database file.
    os.environ["DB_NAME"] = str(db_path)
    # Import and initialize the database after setting the env variable.
    import core.database as db
    db.init_db()
    yield
    # Cleanup: Remove the temporary database file and directory.
    try:
        db_path.unlink()  # remove the temporary database file
    except Exception:
        pass
    shutil.rmtree(str(temp_dir))

# End of tests/conftest.py
