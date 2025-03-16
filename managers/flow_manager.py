# File: managers/flow_manager.py
"""
managers/flow_manager.py
---------------
Summary: Domain logic for multi-step volunteer flows (registration, edit, deletion).
No usage: not a plugin, directly invoked by user_states_manager & API calls.
"""

import logging
from typing import Optional

from managers.user_states_manager import (
    create_flow,
    pause_flow as pause_flow_internal,
    resume_flow as resume_flow_internal,
    get_active_flow as get_active_flow_internal,
    get_flow_step,
    set_flow_step
)
from db.volunteers import get_volunteer_record
from managers.volunteer_manager import VOLUNTEER_MANAGER
from plugins import messages

logger = logging.getLogger(__name__)

# Flow Identifiers
REGISTRATION_FLOW = "volunteer_registration"
EDIT_FLOW = "volunteer_edit"
DELETION_FLOW = "volunteer_deletion"

class FlowManager:
    """
    FlowManager - Encapsulates domain logic for multi-step volunteer flows.
    Exposes start_flow, pause_flow, resume_flow, get_active_flow, handle_flow_input, list_flows.
    """

    def start_flow(self, phone: str, flow_name: str):
        """
        Begin or reset the specified flow for the user, setting initial flow state.
        """
        create_flow(phone, flow_name)

    def pause_flow(self, phone: str, flow_name: str):
        """
        Temporarily pause the specified flow for the user.
        """
        pause_flow_internal(phone, flow_name)

    def resume_flow(self, phone: str, flow_name: str):
        """
        Resume a previously paused flow for the user.
        """
        resume_flow_internal(phone, flow_name)

    def get_active_flow(self, phone: str) -> Optional[str]:
        """
        Return the name of the flow the user is currently in, or None if none.
        """
        return get_active_flow_internal(phone)

    def handle_flow_input(self, phone: str, user_input: str) -> str:
        """
        Process a piece of user input in the currently active flow (if any).
        Dispatches to domain-specific handlers for registration, editing, or deletion.
        Returns any user-facing response message.
        """
        flow_name = self.get_active_flow(phone)
        if not flow_name:
            return ""

        if flow_name == REGISTRATION_FLOW:
            return self._handle_registration_flow(phone, user_input)
        elif flow_name == EDIT_FLOW:
            return self._handle_edit_flow(phone, user_input)
        elif flow_name == DELETION_FLOW:
            return self._handle_deletion_flow(phone, user_input)

        logger.info(f"Unknown flow '{flow_name}' with input '{user_input}'. Pausing.")
        self.pause_flow(phone, flow_name)
        return ""

    def _handle_registration_flow(self, phone: str, user_input: str) -> str:
        record = get_volunteer_record(phone)
        if record:
            self.pause_flow(phone, REGISTRATION_FLOW)
            return messages.ALREADY_REGISTERED_WITH_INSTRUCTIONS.format(name=record["name"])

        stripped_input = user_input.strip().lower()
        if not stripped_input or stripped_input == "skip":
            VOLUNTEER_MANAGER.register_volunteer(phone, "Anonymous", available=True)
            self.pause_flow(phone, REGISTRATION_FLOW)
            return messages.REGISTRATION_COMPLETED_ANONYMOUS
        else:
            # Attempt to set the provided name
            if len(user_input.strip().split()) < 2:
                return messages.REGISTRATION_WELCOME
            response = VOLUNTEER_MANAGER.register_volunteer(
                phone, user_input.strip(), available=True
            )
            self.pause_flow(phone, REGISTRATION_FLOW)
            return response

    def _handle_edit_flow(self, phone: str, user_input: str) -> str:
        record = get_volunteer_record(phone)
        if not record:
            self.pause_flow(phone, EDIT_FLOW)
            self.start_flow(phone, REGISTRATION_FLOW)
            return messages.EDIT_NOT_REGISTERED

        user_input_lower = user_input.strip().lower()
        if not user_input_lower or user_input_lower in ["cancel", "skip"]:
            self.pause_flow(phone, EDIT_FLOW)
            return messages.EDIT_CANCELED_WITH_NAME.format(name=record["name"])

        # Normal name update
        response = VOLUNTEER_MANAGER.register_volunteer(
            phone,
            user_input.strip(),
            available=record["available"]
        )
        self.pause_flow(phone, EDIT_FLOW)
        return response

    def _handle_deletion_flow(self, phone: str, user_input: str) -> str:
        record = get_volunteer_record(phone)
        if not record:
            self.pause_flow(phone, DELETION_FLOW)
            return messages.NOTHING_TO_DELETE

        step_input = user_input.strip().lower()
        current_step = get_flow_step(phone, DELETION_FLOW) or "start"

        if current_step == "start":
            # first prompt
            if step_input in {"yes", "y", "sure"}:
                set_flow_step(phone, DELETION_FLOW, "confirm")
                return messages.DELETION_CONFIRM_PROFILE
            else:
                self.pause_flow(phone, DELETION_FLOW)
                return messages.DELETION_CANCELED

        elif current_step == "confirm":
            # second prompt
            if step_input == "delete":
                confirmation = VOLUNTEER_MANAGER.delete_volunteer(phone)
                self.pause_flow(phone, DELETION_FLOW)
                return messages.VOLUNTEER_DELETED
            else:
                self.pause_flow(phone, DELETION_FLOW)
                return messages.DELETION_CANCELED

        self.pause_flow(phone, DELETION_FLOW)
        return ""

    def list_flows(self, phone: str) -> dict:
        """
        Return a dictionary with "active_flow" and "flows" from user_states_manager.
        """
        from managers.user_states_manager import list_flows
        return list_flows(phone)

# End of managers/flow_manager.py