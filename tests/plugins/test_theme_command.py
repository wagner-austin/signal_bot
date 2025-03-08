#!/usr/bin/env python
"""
tests/plugins/test_theme_command.py - Tests for theme command plugins.
Verifies that theme and plan theme commands return expected placeholder responses.
"""
from plugins.commands.theme import theme_command, plan_theme_command
from core.state import BotStateMachine

def test_theme_command():
    state_machine = BotStateMachine()
    response = theme_command("", "+dummy", state_machine, msg_timestamp=123)
    assert "this week's theme" in response.lower()

def test_plan_theme_command():
    state_machine = BotStateMachine()
    response = plan_theme_command("", "+dummy", state_machine, msg_timestamp=123)
    assert "plan theme:" in response.lower()

# End of tests/plugins/test_theme_command.py