#!/usr/bin/env python
"""
main.py - Main entry point for the Signal bot.
Initializes logging, metrics, and the database, creates an automatic backup on startup,
schedules periodic backups using configurable intervals and retention counts, and then starts the SignalBotService.
Optionally runs the test suite if the --test flag is provided.
"""

import sys
import asyncio
import os
from core.logger_setup import setup_logging

setup_logging()

import core.database
import core.metrics
import logging
from core.signal_bot_service import SignalBotService
from core.database.backup import create_backup, start_periodic_backups
from core.config import BACKUP_INTERVAL, BACKUP_RETENTION_COUNT

logger = logging.getLogger(__name__)

async def main() -> None:
    # Initialize the SQLite database (creates tables if they do not exist)
    core.database.init_db()
    
    # Create an automatic backup at startup
    backup_path = create_backup()
    logger.info(f"Startup backup created at: {backup_path}")
    
    # Schedule periodic backups in the background using configurable interval and retention count.
    asyncio.create_task(start_periodic_backups(interval_seconds=BACKUP_INTERVAL, max_backups=BACKUP_RETENTION_COUNT))
    
    # Fast exit if environment variable is set (used by tests to avoid infinite loop).
    if os.environ.get("FAST_EXIT_FOR_TESTS") == "1":
        logger.info("FAST_EXIT_FOR_TESTS is set, stopping early for test.")
        return
    
    service = SignalBotService()
    await service.run()

if __name__ == "__main__":
    if '--test' in sys.argv:
        from tests.test_all import run_all_tests
        run_all_tests()
    else:
        asyncio.run(main())

# End of main.py