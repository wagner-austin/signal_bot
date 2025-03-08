#!/usr/bin/env python
"""
tests/core/test_event_config.py – Test for core/event_config.py: Verify event details structure.
"""
import core.event_config as event_config

def test_event_details_structure():
    assert "upcoming_event" in event_config.EVENT_DETAILS
    event = event_config.EVENT_DETAILS["upcoming_event"]
    required_keys = ["title", "date", "time", "location", "description", "volunteer_roles"]
    for key in required_keys:
        assert key in event
    assert isinstance(event["volunteer_roles"], dict)

# End of tests/core/test_event_config.py