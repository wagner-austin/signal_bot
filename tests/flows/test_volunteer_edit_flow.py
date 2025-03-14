"""
tests/flows/test_volunteer_edit_flow.py
---------------------------------------
Negative & edge-case tests for the volunteer edit flow.
Ensures cancel, skip, unexpected text, and normal name changes are handled.
Uses FlowManager instead of handle_edit_input.
"""

import pytest
from managers.flow_manager import FlowManager
from managers.user_states_manager import clear_flow_state
from managers.volunteer_manager import VOLUNTEER_MANAGER
from db.volunteers import add_volunteer_record, get_volunteer_record, delete_volunteer_record

@pytest.fixture
def phone_edit():
    return "+9998887772"

@pytest.fixture
def flow_manager():
    return FlowManager()

@pytest.fixture(autouse=True)
def cleanup_edit_flow(phone_edit):
    yield
    clear_flow_state(phone_edit)
    delete_volunteer_record(phone_edit)

def test_unregistered_user_edit_flow(phone_edit, flow_manager):
    """
    If user is not in Volunteers, the flow transitions to registration.
    """
    # ensure no record
    delete_volunteer_record(phone_edit)

    flow_manager.start_flow(phone_edit, flow_manager.EDIT_FLOW)
    response = flow_manager.handle_flow_input(phone_edit, "attempt edit")
    assert "you are not registered" in response.lower()
    assert "starting registration flow" in response.lower()

def test_edit_flow_start_and_cancel(phone_edit, flow_manager):
    """
    Start an edit flow with no input, then user cancels.
    """
    add_volunteer_record(phone_edit, "EditFlowName", [], True, None)
    flow_manager.start_flow(phone_edit, flow_manager.EDIT_FLOW)

    # no user input => triggers "Editing cancelled" or "remain as is" if we handle blank => skip
    r2 = flow_manager.handle_flow_input(phone_edit, "cancel")
    assert "editing cancelled" in r2.lower()

def test_edit_flow_skip_new_name(phone_edit, flow_manager):
    """
    If user types 'skip' instead of a new name, they remain as the old name per code or become Anonymous
    if the code merges skip => "Anonymous." Check final record.
    """
    add_volunteer_record(phone_edit, "OriginalName", [], True, None)
    flow_manager.start_flow(phone_edit, flow_manager.EDIT_FLOW)

    r2 = flow_manager.handle_flow_input(phone_edit, "skip")
    # check final record
    record = get_volunteer_record(phone_edit)
    # The logic in _handle_edit_flow => "skip" => remain as is or "Anonymous" depending on the code
    # The current FlowManager code sets name to "Editing cancelled. You remain registered as..."
    # => no DB update
    assert "editing cancelled" in r2.lower()
    assert record["name"] == "OriginalName", "Should remain original if skip"

def test_edit_flow_normal_name_change(phone_edit, flow_manager):
    """
    Provide a new name, confirm the volunteer record is updated.
    """
    add_volunteer_record(phone_edit, "OldName", [], True, None)
    flow_manager.start_flow(phone_edit, flow_manager.EDIT_FLOW)

    r2 = flow_manager.handle_flow_input(phone_edit, "MyNewName")
    record = get_volunteer_record(phone_edit)
    assert "updated" in r2.lower() or "volunteer" in r2.lower(), \
        "Expected a message about name being updated or newly registered"
    assert record["name"] == "MyNewName"

def test_edit_flow_unexpected_text(phone_edit, flow_manager):
    """
    If user is in the edit flow and provides weird text, we do a normal name update.
    """
    add_volunteer_record(phone_edit, "NameX", [], True, None)
    flow_manager.start_flow(phone_edit, flow_manager.EDIT_FLOW)

    res = flow_manager.handle_flow_input(phone_edit, "???lol???")
    record = get_volunteer_record(phone_edit)
    # The code attempts to register the new name
    assert record["name"] == "???lol???"
    assert "updated" in res.lower() or "volunteer" in res.lower()

# End of tests/flows/test_volunteer_edit_flow.py