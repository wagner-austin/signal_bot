"""
core/database/connection.py - Provides database connection functions.
Establishes and returns a connection to the SQLite database.
"""

import sqlite3
from sqlite3 import Connection
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

# End of core/database/connection.py