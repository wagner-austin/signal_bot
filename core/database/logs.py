"""
core/database/logs.py - Command logs database operations.
Provides functions to log command executions using the general-purpose SQL helper to reduce duplication.
"""

from .helpers import execute_sql

def log_command(sender: str, command: str, args: str) -> None:
    """
    Log a command execution to the database.
    
    Args:
        sender (str): The sender's identifier.
        command (str): The command executed.
        args (str): The arguments passed.
    """
    execute_sql(
        """
        INSERT INTO CommandLogs (sender, command, args)
        VALUES (?, ?, ?)
        """,
        (sender, command, args),
        commit=True
    )

# End of core/database/logs.py