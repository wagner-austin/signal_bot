#!/usr/bin/env python
"""
main.py - Main entry point for the Signal bot.
Initializes logging, backups, plugin loading, and starts the SignalBotService.
"""

import sys
import asyncio
import os
from core.logger_setup import setup_logging

setup_logging()

import db.schema
import core.metrics
import logging
from core.signal_bot_service import SignalBotService
from db.backup import create_backup, start_periodic_backups
from core.config import BACKUP_INTERVAL, BACKUP_RETENTION_COUNT
from plugins.manager import load_plugins, get_all_plugins  # Import plugin loader and getter for logging

logger = logging.getLogger(__name__)

async def main() -> None:
    # Initialize the SQLite database (creates tables if they do not exist)
    db.schema.init_db()
    
    # Create an automatic backup at startup
    backup_path = create_backup()
    logger.info(f"Startup backup created at: {backup_path}")
    
    # Schedule periodic backups in the background using configurable interval and retention count.
    asyncio.create_task(start_periodic_backups(interval_seconds=BACKUP_INTERVAL, max_backups=BACKUP_RETENTION_COUNT))
    
    # Load all plugin modules so that they register their commands.
    load_plugins()
    # (Optional) Log the available plugin commands for verification.
    available_plugins = list(get_all_plugins().keys())
    logger.info(f"Loaded plugins: {available_plugins}")

    # Fast exit if environment variable is set (used by tests to avoid infinite loop).
    if os.environ.get("FAST_EXIT_FOR_TESTS") == "1":
        logger.info("FAST_EXIT_FOR_TESTS is set, stopping early for test.")
        return
    
    service = SignalBotService()
    await service.run()

if __name__ == "__main__":
    asyncio.run(main())

# End of main.py