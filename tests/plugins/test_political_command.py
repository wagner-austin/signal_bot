#!/usr/bin/env python
"""
tests/plugins/test_political_command.py - Tests for political command plugins.
Verifies that political, press, and media commands return expected placeholder responses.
"""
from plugins.commands.political import weekly_update_command, political_command, press_command, media_command
from core.state import BotStateMachine

def test_weekly_update_command():
    state_machine = BotStateMachine()
    response = weekly_update_command("", "+dummy", state_machine, msg_timestamp=123)
    assert "weekly update:" in response.lower()

def test_political_command():
    state_machine = BotStateMachine()
    response = political_command("", "+dummy", state_machine, msg_timestamp=123)
    assert "political" in response.lower()

def test_press_command():
    state_machine = BotStateMachine()
    response = press_command("", "+dummy", state_machine, msg_timestamp=123)
    assert "press" in response.lower()

def test_media_command():
    state_machine = BotStateMachine()
    response = media_command("", "+dummy", state_machine, msg_timestamp=123)
    assert "media" in response.lower()

# End of tests/plugins/test_political_command.py