#!/usr/bin/env python
"""
tests/plugins/test_donate_command.py - Tests for the donate command plugin.
Verifies that the donate_command function handles cash, in-kind, and register subcommands appropriately.
"""

from plugins.commands.donate import donate_command
from core.state import BotStateMachine

def test_donate_cash():
    state_machine = BotStateMachine()
    sender = "+1010101010"
    args = "100 Donation for community event"
    response = donate_command(args, sender, state_machine, msg_timestamp=123)
    # Check that response indicates a donation was logged with an ID.
    assert "Donation logged with ID" in response

def test_donate_in_kind():
    state_machine = BotStateMachine()
    sender = "+2020202020"
    args = "in-kind 10 tables and 50 chairs"
    response = donate_command(args, sender, state_machine, msg_timestamp=123)
    assert "Donation logged with ID" in response

def test_donate_register():
    state_machine = BotStateMachine()
    sender = "+3030303030"
    args = "register paypal Interested in donating via PayPal"
    response = donate_command(args, sender, state_machine, msg_timestamp=123)
    assert "Donation logged with ID" in response

def test_donate_invalid_amount():
    state_machine = BotStateMachine()
    sender = "+4040404040"
    args = "abc Invalid amount test"
    response = donate_command(args, sender, state_machine, msg_timestamp=123)
    # Expect an error message about invalid donation amount.
    assert "Invalid donation amount" in response

def test_donate_usage_instructions():
    state_machine = BotStateMachine()
    sender = "+5050505050"
    args = ""
    response = donate_command(args, sender, state_machine, msg_timestamp=123)
    assert "Usage:" in response

# End of tests/plugins/test_donate_command.py