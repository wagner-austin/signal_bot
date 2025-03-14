#!/usr/bin/env python
"""
File: db/stats.py
-----------------
Database statistics and tracking.
Provides functions to retrieve current database statistics via StatsRepository.
"""

from db.repository import StatsRepository

def get_database_stats():
    """
    Get statistics of the current database, now leveraging StatsRepository.

    Returns:
        dict: A dictionary with two keys:
              'tables' - a mapping of table names to their row counts,
              'schema_version' - the current migration version from the SchemaVersion table (if available).
    """
    repo = StatsRepository()
    stats = {"tables": {}, "schema_version": None}

    tables = repo.get_table_names()
    for t in tables:
        try:
            stats["tables"][t] = repo.get_row_count(t)
        except Exception as e:
            stats["tables"][t] = f"Error: {str(e)}"

    stats["schema_version"] = repo.get_schema_version()
    return stats

# End of db/stats.py