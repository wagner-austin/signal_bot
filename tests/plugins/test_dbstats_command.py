#!/usr/bin/env python
"""
tests/plugins/test_dbstats_command.py - Tests for the dbstats command plugin.
Verifies that the dbstats_command returns valid database statistics.
"""

from plugins.commands.dbstats import dbstats_command
from core.state import BotStateMachine

def test_dbstats_command():
    state_machine = BotStateMachine()
    sender = "+1111111111"
    response = dbstats_command("", sender, state_machine, msg_timestamp=123)
    # Check that the response includes key phrases for stats
    assert "Database Statistics:" in response
    assert "Table Row Counts:" in response

# End of tests/plugins/test_dbstats_command.py