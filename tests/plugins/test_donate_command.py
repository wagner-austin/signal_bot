#!/usr/bin/env python
"""
tests/plugins/test_donate_command.py - Tests for the donate command plugin.
Verifies both normal donation paths (cash, in-kind, register) and usage instructions.
"""

from plugins.commands.donate import donate_command
from core.state import BotStateMachine


def test_donate_no_args_shows_usage():
    """
    Test that calling donate_command with no arguments returns usage instructions.
    """
    state_machine = BotStateMachine()
    sender = "+1010101010"
    response = donate_command("", sender, state_machine, msg_timestamp=123)
    assert "Usage:" in response
    assert "donate <amount> <description>" in response
    assert "donate in-kind <description>" in response
    assert "donate register <method> [<description>]" in response


def test_donate_cash():
    """
    Tests a normal cash donation path.
    """
    state_machine = BotStateMachine()
    sender = "+1010101010"
    args = "100 Donation for community event"
    response = donate_command(args, sender, state_machine, msg_timestamp=123)
    assert "Donation logged with ID" in response


def test_donate_in_kind():
    """
    Tests an in-kind donation path.
    """
    state_machine = BotStateMachine()
    sender = "+2020202020"
    args = "in-kind 10 tables and 50 chairs"
    response = donate_command(args, sender, state_machine, msg_timestamp=123)
    assert "Donation logged with ID" in response


def test_donate_register():
    """
    Tests registering a donation method (like PayPal).
    """
    state_machine = BotStateMachine()
    sender = "+3030303030"
    args = "register paypal Interested in donating via PayPal"
    response = donate_command(args, sender, state_machine, msg_timestamp=123)
    assert "Donation logged with ID" in response

# End of tests/plugins/test_donate_command.py