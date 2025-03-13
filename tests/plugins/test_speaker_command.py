#!/usr/bin/env python
"""
tests/plugins/test_speaker_command.py - Tests for speaker command plugin.
Verifies handling of missing fields and proper addition/removal of speakers.
"""

import pytest
from plugins.commands.speaker import add_speaker_command, remove_speaker_command
from core.state import BotStateMachine
from managers.event_manager import create_event

@pytest.fixture
def state_machine():
    return BotStateMachine()

@pytest.fixture
def sample_event():
    ev_id = create_event("Sample Event", "2025-01-01", "10AM", "Test Venue", "Description")
    return ev_id

def test_add_speaker_missing_fields(state_machine, sample_event):
    response = add_speaker_command(f"EventID: {sample_event}, Name: SpeakerOne", "+dummy", state_machine)
    from core.plugin_usage import USAGE_ADD_SPEAKER
    assert USAGE_ADD_SPEAKER.lower() in response.lower()

def test_add_speaker_success(state_machine, sample_event):
    response = add_speaker_command(
        f"EventID: {sample_event}, Name: GoodSpeaker, Topic: GreatTopic",
        "+dummy",
        state_machine
    )
    assert "assigned to event id" in response.lower()

def test_remove_speaker_non_existent(state_machine, sample_event):
    response = remove_speaker_command(f"EventID: {sample_event}, Name: NoSuchSpeaker", "+dummy", state_machine)
    assert "removed from event id" in response.lower()

def test_add_speaker_no_eventid(state_machine):
    response = add_speaker_command("Name: Mystery, Topic: Something", "+dummy", state_machine)
    if "no upcoming events found" not in response.lower():
        assert "assigned to event id" in response.lower() or "no upcoming events found" in response.lower()

# End of tests/plugins/test_speaker_command.py