#!/usr/bin/env python
"""
core/database/stats.py - Database statistics and tracking.
Provides functions to retrieve current database statistics, including table row counts and the current schema version.
"""

from core.database.connection import get_connection

def get_database_stats():
    """
    Get statistics of the current database.

    Returns:
        dict: A dictionary with two keys:
              'tables' - a mapping of table names to their row counts,
              'schema_version' - the current migration version from the SchemaVersion table (if available).
    """
    stats = {"tables": {}, "schema_version": None}
    conn = get_connection()
    cursor = conn.cursor()
    
    # Retrieve all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row["name"] for row in cursor.fetchall()]
    
    # Count rows for each table
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count_row = cursor.fetchone()
            stats["tables"][table] = count_row["count"] if count_row else 0
        except Exception as e:
            stats["tables"][table] = f"Error: {str(e)}"
    
    # Get the current schema version if SchemaVersion table exists
    if "SchemaVersion" in tables:
        cursor.execute("SELECT version FROM SchemaVersion")
        row = cursor.fetchone()
        stats["schema_version"] = row["version"] if row else None
    
    conn.close()
    return stats

# End of core/database/stats.py