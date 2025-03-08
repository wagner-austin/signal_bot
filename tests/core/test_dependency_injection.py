#!/usr/bin/env python
"""
tests/core/test_dependency_injection.py - Tests for dependency injection.
This module verifies that critical modules accept dependencies (such as connection providers and loggers)
and use them instead of global instances.
"""

import sqlite3
import asyncio
import logging
import pytest
from core.database.repository import BaseRepository
from core.signal_client import send_message
from managers.message.message_dispatcher import dispatch_message
from parsers.message_parser import ParsedMessage
from core.state import BotStateMachine

# -------------------
# Dummy Connection Provider Tests
# -------------------

# Create a persistent in-memory connection.
_persistent_conn = sqlite3.connect(":memory:")
_persistent_conn.row_factory = sqlite3.Row
_persistent_conn.execute("CREATE TABLE Dummy (id INTEGER PRIMARY KEY AUTOINCREMENT, value TEXT)")
_persistent_conn.commit()

class DummyConnectionWrapper:
    """
    DummyConnectionWrapper - Wraps a sqlite3.Connection to override the close() method.
    """
    def __init__(self, conn):
        self._conn = conn
    def __getattr__(self, attr):
        return getattr(self._conn, attr)
    def close(self):
        # Override close to do nothing.
        pass

def dummy_connection_provider():
    return DummyConnectionWrapper(_persistent_conn)

class DummyRepository(BaseRepository):
    def __init__(self, connection_provider):
        super().__init__("Dummy", primary_key="id", connection_provider=connection_provider)

def test_dummy_repository_crud():
    repo = DummyRepository(dummy_connection_provider)
    # Create a record
    rec_id = repo.create({"value": "test_value"})
    assert rec_id > 0
    # Retrieve the record
    record = repo.get_by_id(rec_id)
    assert record is not None
    assert record["value"] == "test_value"
    # Update the record
    repo.update(rec_id, {"value": "updated_value"})
    updated = repo.get_by_id(rec_id)
    assert updated["value"] == "updated_value"
    # List records with filter
    records = repo.list_all(filters={"value": "updated_value"})
    assert any(r["id"] == rec_id for r in records)
    # Delete the record
    repo.delete(rec_id)
    assert repo.get_by_id(rec_id) is None

# -------------------
# Dummy Logger for Dependency Injection Tests
# -------------------

class ListHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []
    def emit(self, record):
        self.records.append(record.getMessage())

@pytest.fixture
def dummy_logger():
    logger = logging.getLogger("dummy_logger")
    logger.setLevel(logging.DEBUG)
    handler = ListHandler()
    logger.addHandler(handler)
    yield logger, handler
    logger.removeHandler(handler)

# -------------------
# Dummy PendingActions and Volunteer Manager for Testing dispatch_message
# -------------------

class DummyPendingActions:
    def has_event_creation(self, sender: str) -> bool:
        return False
    def clear_event_creation(self, sender: str) -> None:
        pass
    def has_deletion(self, sender: str) -> bool:
        return False
    def get_deletion(self, sender: str):
        return None
    def clear_deletion(self, sender: str) -> None:
        pass
    def has_registration(self, sender: str) -> bool:
        return False
    def get_registration(self, sender: str):
        return None
    def clear_registration(self, sender: str) -> None:
        pass

class DummyVolunteerManager:
    pass  # Not used in this test

# -------------------
# Test Logger Injection in send_message
# -------------------

@pytest.mark.asyncio
async def test_send_message_with_dummy_logger(monkeypatch, dummy_logger):
    logger, handler = dummy_logger

    async def dummy_async_run(args, stdin_input=None):
        return "dummy output"
    monkeypatch.setattr("core.signal_client.async_run_signal_cli", dummy_async_run)
    await send_message(
        to_number="+1111111111",
        message="Test message",
        logger=logger
    )
    # Check that our dummy logger captured an info log.
    found = any("Sent to +1111111111: Test message" in msg for msg in handler.records)
    assert found

# -------------------
# Test Logger Injection in dispatch_message
# -------------------

def test_dispatch_message_with_dummy_logger(monkeypatch, dummy_logger):
    logger, handler = dummy_logger
    # Create a dummy ParsedMessage with an unknown command.
    parsed = ParsedMessage(
        sender="+1234567890",
        body="@bot unknowncommand",
        timestamp=123,
        group_id=None,
        reply_to=None,
        message_timestamp=None,
        command="unknowncommand",
        args=""
    )
    state_machine = BotStateMachine()
    # Provide dummy pending actions and volunteer manager.
    dummy_pending = DummyPendingActions()
    dummy_volunteer_manager = DummyVolunteerManager()
    monkeypatch.setattr("plugins.manager.get_all_plugins", lambda: {})
    response = dispatch_message(parsed, "+1234567890", state_machine,
                                pending_actions=dummy_pending,
                                volunteer_manager=dummy_volunteer_manager,
                                msg_timestamp=123, logger=logger)
    # Since no plugin is found, response should be empty.
    assert response == ""
    # Now, create a faulty plugin that raises an exception.
    def faulty_plugin(args, sender, state_machine, msg_timestamp=None):
        raise Exception("Test error")
    from plugins.manager import alias_mapping, plugin_registry
    alias_mapping["faulty"] = "faulty"
    plugin_registry["faulty"] = {"function": faulty_plugin, "aliases": ["faulty"], "help_visible": True}
    parsed.command = "faulty"
    response_error = dispatch_message(parsed, "+1234567890", state_machine,
                                      pending_actions=dummy_pending,
                                      volunteer_manager=dummy_volunteer_manager,
                                      msg_timestamp=123, logger=logger)
    assert "internal error" in response_error.lower()
    # Check that the logger recorded an exception message.
    assert any("Error executing plugin for command" in msg for msg in handler.records)
    # Cleanup faulty plugin registration to avoid affecting other tests.
    alias_mapping.pop("faulty", None)
    plugin_registry.pop("faulty", None)

# End of tests/core/test_dependency_injection.py