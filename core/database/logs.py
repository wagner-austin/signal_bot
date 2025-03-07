"""
core/database/logs.py - Command logs database operations.
Provides functions to log command executions using a context manager for connection handling.
"""

from .connection import db_connection

def log_command(sender: str, command: str, args: str) -> None:
    """
    Log a command execution to the database.
    
    Args:
        sender (str): The sender's identifier.
        command (str): The command executed.
        args (str): The arguments passed.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO CommandLogs (sender, command, args)
        VALUES (?, ?, ?)
        """, (sender, command, args))
        conn.commit()

# End of core/database/logs.py