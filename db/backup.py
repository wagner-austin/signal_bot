#!/usr/bin/env python
"""
db/backup.py - Database backup and restore utilities.
Provides functions to create a backup snapshot of the current database, automatically clean up old backups
using a configurable retention count, and schedule periodic backups using a configurable interval.
Changes:
 - Added an info-level log message upon successful backup creation.
 - Updated periodic backup to handle exceptions and log warnings on failure.
 - Updated restore_backup to check for truncated backups (≤ 16 bytes) and log as invalid/corrupted.
"""

import os
import shutil
from datetime import datetime
import asyncio
import logging
from core.config import DB_NAME, BACKUP_INTERVAL, BACKUP_RETENTION_COUNT

logger = logging.getLogger(__name__)

# Define the backups directory relative to the DB_NAME location.
BACKUP_DIR = os.path.join(os.path.dirname(DB_NAME), "backups")

def _generate_backup_filename() -> str:
    """
    Generates a unique backup filename using the current date-time second.
    If multiple backups occur in the same second, appends a numeric suffix.
    """
    base_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = 0
    while True:
        filename = f"backup_{base_timestamp}"
        if suffix:
            filename += f"_{suffix}"
        filename += ".db"
        fullpath = os.path.join(BACKUP_DIR, filename)
        if not os.path.exists(fullpath):
            return filename
        suffix += 1

def create_backup() -> str:
    """
    Create a backup of the current database and enforce the retention policy based on BACKUP_RETENTION_COUNT.

    Returns:
        str: The file path of the created backup, or an empty string if creation failed.
    """
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
    except OSError as e:
        logger.warning(f"Failed to create backup directory '{BACKUP_DIR}'. Error: {e}")
        return ""
    
    backup_filename = _generate_backup_filename()
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    try:
        shutil.copyfile(DB_NAME, backup_path)
        cleanup_backups(max_backups=BACKUP_RETENTION_COUNT)
        logger.info(f"Backup created at: {backup_path}")
        return backup_path
    except Exception as e:
        logger.warning(f"Failed to create backup file at '{backup_path}'. Error: {e}")
        return ""

def cleanup_backups(max_backups: int = BACKUP_RETENTION_COUNT) -> None:
    """
    Enforce the retention policy by keeping only the latest max_backups files in the backup directory.

    Args:
        max_backups (int): Maximum number of backup files to retain.
    """
    if not os.path.exists(BACKUP_DIR):
        return

    # If max_backups is zero or negative, remove all backups.
    if max_backups <= 0:
        logger.warning(f"Received non-positive max_backups={max_backups}. Removing all backups.")
        max_backups = 0

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
    Uses a minimal signature check to confirm it's valid SQLite and ensures the backup file is not truncated.

    Args:
        backup_filename (str): The name of the backup file (found in the backups folder).

    Returns:
        bool: True if restoration is successful, False otherwise.
    """
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    if not os.path.exists(backup_path):
        return False

    # Check for valid SQLite signature in first 16 bytes: "SQLite format 3\000"
    try:
        with open(backup_path, "rb") as f:
            header = f.read(16)
        if not header.startswith(b"SQLite format 3\000"):
            logger.warning(f"Cannot restore from backup '{backup_filename}': invalid or corrupted SQLite file.")
            return False
        # Check if the file is truncated (i.e., only header and no additional content)
        if os.path.getsize(backup_path) <= 16:
            logger.warning(f"Cannot restore from backup '{backup_filename}': invalid or corrupted SQLite file.")
            return False
    except Exception as e:
        logger.warning(f"Cannot restore from backup '{backup_filename}': error reading file. Error: {e}")
        return False

    try:
        shutil.copyfile(backup_path, DB_NAME)
    except Exception as e:
        logger.warning(f"Failed to restore backup '{backup_filename}' to '{DB_NAME}'. Error: {e}")
        return False

    return True

async def start_periodic_backups(interval_seconds: int = BACKUP_INTERVAL, max_backups: int = BACKUP_RETENTION_COUNT) -> None:
    """
    Schedule periodic backups at the specified interval.

    Args:
        interval_seconds (int): Time interval between backups in seconds (configurable via BACKUP_INTERVAL).
        max_backups (int): Maximum number of backups to retain (configurable via BACKUP_RETENTION_COUNT).

    Changes:
        - Added error handling to ensure a single backup failure does not kill the periodic backup task.
    """
    while True:
        try:
            create_backup()
        except Exception as e:
            logger.warning(f"Periodic backup failed: {e}")
        await asyncio.sleep(interval_seconds)

# End of db/backup.py