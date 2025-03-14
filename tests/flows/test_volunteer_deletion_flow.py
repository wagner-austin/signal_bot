"""
tests/flows/test_volunteer_deletion_flow.py
-------------------------------------------
Negative & edge-case tests for the volunteer deletion flow.
Now uses FlowManager instead of old handle_deletion_input.
"""

import pytest
from managers.flow_manager import FlowManager
from managers.user_states_manager import clear_flow_state, get_active_flow
from managers.volunteer_manager import VOLUNTEER_MANAGER
from db.volunteers import add_volunteer_record, delete_volunteer_record, get_volunteer_record

@pytest.fixture
def mock_phone():
    return "+9998887771"

@pytest.fixture
def flow_manager():
    return FlowManager()

@pytest.fixture(autouse=True)
def cleanup_flows(mock_phone):
    yield
    clear_flow_state(mock_phone)
    delete_volunteer_record(mock_phone)

def test_already_deleted_user_deletion_flow(mock_phone, flow_manager):
    """
    If the user is not in Volunteers or is already deleted,
    the flow's first input should see that record is None and return a "not registered" message.
    """
    delete_volunteer_record(mock_phone)  # ensure user is not in Volunteers
    flow_manager.start_flow(mock_phone, flow_manager.DELETION_FLOW)

    # step "initial"
    response = flow_manager.handle_flow_input(mock_phone, "delete")
    # Because user_input_lower = "delete" is not in {"yes", "y", "sure"}, flow will skip to "Deletion cancelled."
    # Actually, check the code: record is None => "You are not currently registered; nothing to delete."
    assert "not currently registered" in response.lower()

def test_contradictory_first_step(mock_phone, flow_manager):
    """
    Test user providing random text at the initial flow step.
    """
    add_volunteer_record(mock_phone, "DeletionFlowTest", ["FlowSkill"], True, None)
    flow_manager.start_flow(mock_phone, flow_manager.DELETION_FLOW)

    # user provides random text => triggers 'Deletion cancelled.'
    r1 = flow_manager.handle_flow_input(mock_phone, "randomstuff")
    assert "deletion cancelled" in r1.lower()

def test_confirm_step_cancelled(mock_phone, flow_manager):
    """
    Once user says 'yes' in the initial step, they go to confirm step.
    If they then type random text, it cancels.
    """
    add_volunteer_record(mock_phone, "DeletionFlowTest2", [], True, None)
    flow_manager.start_flow(mock_phone, flow_manager.DELETION_FLOW)

    # user says 'yes' => step => confirm
    flow_manager.handle_flow_input(mock_phone, "yes")

    # random text => "Deletion cancelled."
    r3 = flow_manager.handle_flow_input(mock_phone, "nope")
    assert "deletion cancelled" in r3.lower()

def test_confirm_step_proceeds(mock_phone, flow_manager):
    """
    Normal path: user eventually says 'delete' at confirm => record is deleted.
    """
    add_volunteer_record(mock_phone, "DeletionFlowTest3", [], True, None)
    flow_manager.start_flow(mock_phone, flow_manager.DELETION_FLOW)

    # initial => yes => confirm
    flow_manager.handle_flow_input(mock_phone, "yes")
    r3 = flow_manager.handle_flow_input(mock_phone, "delete")
    # check final message
    assert "deleted" in r3.lower()

def test_multiple_flows_same_user(mock_phone, flow_manager):
    """
    Starting a second flow overwrites the active flow for that user.
    """
    add_volunteer_record(mock_phone, "DeletionFlowTest4", [], True, None)
    flow_manager.start_flow(mock_phone, flow_manager.DELETION_FLOW)

    active1 = get_active_flow(mock_phone)
    assert active1 == flow_manager.DELETION_FLOW

    # Then create another flow forcibly
    flow_manager.start_flow(mock_phone, "some_other_flow")
    active2 = get_active_flow(mock_phone)
    assert active2 == "some_other_flow"

# End of tests/flows/test_volunteer_deletion_flow.py