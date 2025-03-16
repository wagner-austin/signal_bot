"""
File: tests/plugins/test_speaker_command.py
------------------------------------------
Tests for speaker command plugins. Verifies handling of missing fields and proper addition/removal of speakers.
"""

import pytest
from core.state import BotStateMachine
from managers.event_manager import create_event
from plugins.manager import get_plugin

@pytest.fixture
def state_machine():
    return BotStateMachine()

@pytest.fixture
def sample_event():
    ev_id = create_event("Sample Event", "2025-01-01", "10AM", "Test Venue", "Description")
    return ev_id

def test_add_speaker_missing_fields(state_machine, sample_event):
    add_speaker_plugin = get_plugin("add speaker")
    response = add_speaker_plugin(f"default EventID: {sample_event}, Name: SpeakerOne", "+dummy", state_machine)
    from plugins.plugin_usage import USAGE_ADD_SPEAKER
    assert USAGE_ADD_SPEAKER.lower() in response.lower()

def test_add_speaker_success(state_machine, sample_event):
    add_speaker_plugin = get_plugin("add speaker")
    response = add_speaker_plugin(
        f"default EventID: {sample_event}, Name: GoodSpeaker, Topic: GreatTopic",
        "+dummy",
        state_machine
    )
    assert "assigned to event id" in response.lower()

def test_remove_speaker_non_existent(state_machine, sample_event):
    remove_speaker_plugin = get_plugin("remove speaker")
    response = remove_speaker_plugin(
        f"default EventID: {sample_event}, Name: NoSuchSpeaker",
        "+dummy",
        state_machine
    )
    assert "removed from event id" in response.lower()

def test_add_speaker_no_eventid(state_machine):
    add_speaker_plugin = get_plugin("add speaker")
    response = add_speaker_plugin(
        "default Name: Mystery, Topic: Something",
        "+dummy",
        state_machine
    )
    if "no upcoming events found" not in response.lower():
        assert "assigned to event id" in response.lower() or "no upcoming events found" in response.lower()

# End of tests/plugins/test_speaker_command.py