#!/usr/bin/env python
"""
core/database/backup.py - Database backup and restore utilities with retention and periodic scheduling.
Provides functions to create a backup snapshot of the current database, automatically clean up old backups (keeping only the latest 10),
and schedule periodic backups.
Backups are saved in the 'backups' folder with a timestamp appended.
"""

import os
import shutil
from datetime import datetime
import asyncio
from core.config import DB_NAME

# Define the backups directory relative to the DB_NAME location.
BACKUP_DIR = os.path.join(os.path.dirname(DB_NAME), "backups")

def create_backup() -> str:
    """
    Create a backup of the current database and enforce the retention policy (max 10 backups).

    Returns:
        str: The file path of the created backup.
    """
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    shutil.copyfile(DB_NAME, backup_path)
    cleanup_backups(max_backups=10)
    return backup_path

def cleanup_backups(max_backups: int = 10) -> None:
    """
    Enforce the retention policy by keeping only the latest max_backups files in the backup directory.

    Args:
        max_backups (int): Maximum number of backup files to retain.
    """
    if not os.path.exists(BACKUP_DIR):
        return
    backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".db")]
    backups.sort()  # Sorted by filename (timestamp order)
    while len(backups) > max_backups:
        oldest = backups.pop(0)
        try:
            os.remove(os.path.join(BACKUP_DIR, oldest))
        except Exception:
            pass

def list_backups() -> list:
    """
    List all backup files in the backup directory.

    Returns:
        list: A sorted list of backup file names.
    """
    if not os.path.exists(BACKUP_DIR):
        return []
    backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".db")]
    backups.sort()
    return backups

def restore_backup(backup_filename: str) -> bool:
    """
    Restore the database from a specified backup file.
    
    Args:
        backup_filename (str): The name of the backup file (found in the backups folder).

    Returns:
        bool: True if restoration is successful, False otherwise.
    """
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    if not os.path.exists(backup_path):
        return False
    shutil.copyfile(backup_path, DB_NAME)
    return True

async def start_periodic_backups(interval_seconds: int = 3600, max_backups: int = 10) -> None:
    """
    Schedule periodic backups at the specified interval. This function runs indefinitely.
    
    Args:
        interval_seconds (int): Time interval between backups in seconds.
        max_backups (int): Maximum number of backups to retain.
    """
    while True:
        create_backup()
        await asyncio.sleep(interval_seconds)

# End of core/database/backup.py