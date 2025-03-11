#!/usr/bin/env python
"""
tests/plugins/test_donate_command.py - Tests for the donate command plugin.
Verifies normal donation paths (cash, in-kind, register) and usage instructions,
and includes additional edge-case tests for negative and extremely large donation amounts.
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


def test_donate_negative_amount():
    """
    Tests logging a negative cash donation (edge case).
    Verifies that a negative amount does not break the parsing or insertion logic.
    """
    state_machine = BotStateMachine()
    sender = "+4040404041"
    args = "-100 Malicious donation"
    response = donate_command(args, sender, state_machine, msg_timestamp=123)
    assert "Donation logged with ID" in response


def test_donate_extremely_large_amount():
    """
    Tests logging an extremely large cash donation (edge case).
    Verifies that an exorbitantly large donation amount is accepted without errors.
    """
    state_machine = BotStateMachine()
    sender = "+4040404042"
    args = "1e12 Extremely large donation"
    response = donate_command(args, sender, state_machine, msg_timestamp=123)
    assert "Donation logged with ID" in response

# End of tests/plugins/test_donate_command.py