#!/usr/bin/env python
"""
test_donate_command.py
----------------------
Tests the donate command plugin for normal donation paths (cash, in-kind, register).
Negative/edge donation tests are now in test_plugin_negatives.py.
"""

from plugins.commands.donate import donate_command
from core.state import BotStateMachine

def test_donate_cash():
    state_machine = BotStateMachine()
    sender = "+1010101010"
    args = "100 Donation for community event"
    response = donate_command(args, sender, state_machine, msg_timestamp=123)
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

# End of tests/plugins/commands/test_donate_command.py