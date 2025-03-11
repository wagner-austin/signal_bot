#!/usr/bin/env python
"""
tests/core/test_periodic_backup.py --- Tests for periodic backup scheduling, error handling, and cleanup efficiency.
Verifies that the periodic backup function creates backups at defined intervals, handles backup errors gracefully,
and efficiently cleans up a large number of backup files.
Changes:
 - Added a test to simulate an exception during backup creation and confirm that it logs a warning while continuing.
 - Added a stress test to create 100 dummy backups and ensure cleanup_backups(max_backups=5) reduces them to 5.
"""

import asyncio
import os
import shutil
import time
import pytest
import logging
from tests.async_helpers import override_async_sleep
from core.database.backup import start_periodic_backups, list_backups, cleanup_backups, BACKUP_DIR

# New test: Simulate backup failure and ensure error is handled gracefully
@pytest.mark.asyncio
async def test_periodic_backup_error_handling(monkeypatch, caplog):
    try:
        if os.path.exists(BACKUP_DIR):
            shutil.rmtree(BACKUP_DIR)
        os.makedirs(BACKUP_DIR)
        
        call_count = 0
        def fake_create_backup():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise OSError("Simulated copy failure")
            return "/fake/backup.db"
        
        # Patch create_backup in the backup module
        monkeypatch.setattr("core.database.backup.create_backup", fake_create_backup)
        
        async with override_async_sleep(monkeypatch, scale=0.01):
            task = asyncio.create_task(start_periodic_backups(interval_seconds=0.1, max_backups=10))
            # Allow a few iterations
            await asyncio.sleep(0.5)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Verify that fake_create_backup was called multiple times
        assert call_count >= 2, "Expected multiple calls to create_backup despite an initial failure."
        # Check that a warning was logged for the simulated failure
        warning_logs = [record.message for record in caplog.records if "Periodic backup failed:" in record.message]
        assert any("Simulated copy failure" in message for message in warning_logs), "Expected a warning for the simulated backup failure."
    finally:
        if os.path.exists(BACKUP_DIR):
            shutil.rmtree(BACKUP_DIR)

# New test: Stress test cleanup with a very large number of backups
def test_cleanup_large_number_of_backups():
    try:
        if os.path.exists(BACKUP_DIR):
            shutil.rmtree(BACKUP_DIR)
        os.makedirs(BACKUP_DIR)
        
        # Create 100 dummy backup files
        for i in range(100):
            filename = f"stress_backup_{i:03d}.db"
            filepath = os.path.join(BACKUP_DIR, filename)
            with open(filepath, "w") as f:
                f.write("dummy")
        
        # Ensure we have 100 backups before cleanup
        backups_before = list_backups()
        assert len(backups_before) == 100, f"Expected 100 backups, found {len(backups_before)}."
        
        # Perform cleanup to retain only 5 backups
        cleanup_backups(max_backups=5)
        backups_after = list_backups()
        assert len(backups_after) == 5, f"Expected 5 backups after cleanup, found {len(backups_after)}."
    finally:
        if os.path.exists(BACKUP_DIR):
            shutil.rmtree(BACKUP_DIR)

# Existing test remains unchanged
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