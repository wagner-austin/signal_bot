#!/usr/bin/env python
"""
core/database/stats.py - Database statistics and tracking.
Provides functions to retrieve current database statistics, including table row counts (excluding system and unwanted tables)
and the current schema version. This centralizes the stats calculation for use in CLI commands.
"""

from core.database.connection import get_connection

def get_database_stats():
    """
    Get statistics of the current database.

    Returns:
        dict: A dictionary with two keys:
              'tables' - a mapping of table names to their row counts (excluding sqlite_sequence, SchemaVersion, and CommandLogs),
              'schema_version' - the current migration version from the SchemaVersion table (if available).
    """
    stats = {"tables": {}, "schema_version": None}
    conn = get_connection()
    cursor = conn.cursor()
    
    # Exclude system and unwanted tables from stats
    excluded_tables = {"sqlite_sequence", "SchemaVersion", "CommandLogs"}
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row["name"] for row in cursor.fetchall() if row["name"] not in excluded_tables]
    
    # Count rows for each included table
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count_row = cursor.fetchone()
            stats["tables"][table] = count_row["count"] if count_row else 0
        except Exception as e:
            stats["tables"][table] = f"Error: {str(e)}"
    
    # Retrieve schema version from SchemaVersion if it exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='SchemaVersion'")
    if cursor.fetchone():
        cursor.execute("SELECT version FROM SchemaVersion")
        row = cursor.fetchone()
        stats["schema_version"] = row["version"] if row else None
    
    conn.close()
    return stats

# End of core/database/stats.py