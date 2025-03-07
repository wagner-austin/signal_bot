"""
core/database/logs.py - Command logs database operations.
Provides functions to log command executions.
"""

from .connection import get_connection

def log_command(sender: str, command: str, args: str) -> None:
    """
    Log a command execution to the database.
    
    Args:
        sender (str): The sender's identifier.
        command (str): The command executed.
        args (str): The arguments passed.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO CommandLogs (sender, command, args)
    VALUES (?, ?, ?)
    """, (sender, command, args))
    conn.commit()
    conn.close()

# End of core/database/logs.py