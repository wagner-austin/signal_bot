#!/usr/bin/env python
"""
tests/core/test_periodic_backup.py - Tests for periodic backup scheduling.
Verifies that the periodic backup function creates backups at defined intervals in an adaptive manner.
Uses a common async helper to override asyncio.sleep for faster test execution.
Ensures that backup files are cleaned up reliably even if the test fails.
"""

import asyncio
import os
import shutil
import time
import pytest
from tests.async_helpers import override_async_sleep
from core.database.backup import start_periodic_backups, list_backups, BACKUP_DIR

@pytest.mark.asyncio
async def test_periodic_backup_once(monkeypatch):
    try:
        # Ensure a clean backup directory before starting the test
        if os.path.exists(BACKUP_DIR):
            shutil.rmtree(BACKUP_DIR)
        
        async with override_async_sleep(monkeypatch, scale=0.01):
            # Start periodic backups with a very short interval for testing purposes.
            task = asyncio.create_task(start_periodic_backups(interval_seconds=0.1, max_backups=10))
            
            # Poll for backup creation with an adaptive timeout
            start_time = time.time()
            timeout = 0.5  # maximum wait time in real seconds
            backups = []
            while time.time() - start_time < timeout:
                backups = list_backups()
                if backups:
                    break
                await asyncio.sleep(0.01)  # small delay to yield control
            
            # Cancel the periodic backup task
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        # Verify that at least one backup has been created
        assert len(backups) >= 1, "No backups were created within the timeout period."
    finally:
        if os.path.exists(BACKUP_DIR):
            shutil.rmtree(BACKUP_DIR)

# End of tests/core/test_periodic_backup.py