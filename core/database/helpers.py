"""
core/database/helpers.py - Provides helper functions for executing SQL queries.
Encapsulates common database operations to reduce duplication.
"""

from .connection import db_connection

def execute_sql(query: str, params: tuple = (), commit: bool = False, fetchone: bool = False, fetchall: bool = False):
    """
    Execute a SQL query with the given parameters.

    Args:
        query (str): The SQL query to execute.
        params (tuple, optional): Parameters for the SQL query.
        commit (bool, optional): Whether to commit the transaction.
        fetchone (bool, optional): If True, return one row.
        fetchall (bool, optional): If True, return all rows.

    Returns:
        The result of fetchone or fetchall if specified; otherwise, None.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = None
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        if commit:
            conn.commit()
        return result

# End of core/database/helpers.py