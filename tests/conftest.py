"""
tests/conftest.py - Pytest configuration and fixtures.
Immediately overrides the DB_NAME environment variable with a temporary database path
to ensure tests run in isolation from the production database.
After tests, the temporary database file is removed and DB_NAME is unset.
"""

import os
import tempfile
import pytest

# Immediately override DB_NAME for tests before any other modules are imported.
# This ensures that all modules (including those imported during test collection)
# will use the temporary test database.
fd, temp_db_path = tempfile.mkstemp(prefix="bot_data_test_", suffix=".db")
os.close(fd)  # Close the file descriptor; sqlite3 will manage the file.
os.environ["DB_NAME"] = temp_db_path

@pytest.fixture(scope="session", autouse=True)
def test_database():
    """
    Creates and initializes a temporary database for testing.
    The DB_NAME environment variable is set to a temporary file, ensuring
    tests run without affecting the production database.
    After tests complete, the temporary database file is removed and DB_NAME is unset.
    """
    # Import and initialize the database after setting the env variable.
    import core.database as db
    db.init_db()
    
    yield

    # Cleanup: Remove the temporary database file.
    try:
        os.remove(temp_db_path)
    except Exception:
        pass
    # Unset DB_NAME so production code reverts to default (if not set externally).
    os.environ.pop("DB_NAME", None)

# End of tests/conftest.py