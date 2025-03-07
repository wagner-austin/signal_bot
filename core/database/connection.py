"""
core/database/connection.py - Provides database connection functions.
Establishes and returns a connection to the SQLite database and includes a context manager for automatic handling.
"""

import sqlite3
from sqlite3 import Connection
from contextlib import contextmanager
from core.config import DB_NAME

def get_connection() -> Connection:
    """
    Establish and return a connection to the SQLite database.
    
    Returns:
        Connection: The SQLite connection object.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def db_connection():
    """
    Context manager for SQLite database connection.
    
    Yields:
        Connection: The SQLite connection object with row_factory set.
    Ensures that the connection is closed after usage.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# End of core/database/connection.py