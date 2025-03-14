#!/usr/bin/env python
"""
managers/flow_manager.py
------------------------
Centralized flow management for multi-step volunteer flows: registration, edit, and deletion.
All user inputs for these flows are handled here; no partial checks remain in plugin commands.
"""

import logging
from managers.user_states_manager import (
    get_active_flow as userstate_get_active_flow,
    create_flow,
    pause_flow,
    set_flow_step,
    get_flow_step
)
from managers.volunteer_manager import VOLUNTEER_MANAGER
from db.volunteers import get_volunteer_record

logger = logging.getLogger(__name__)

class FlowManager:
    """
    FlowManager - Orchestrates multi-step flows for volunteer registration, editing, and deletion.
    """

    REGISTRATION_FLOW = "volunteer_registration"
    EDIT_FLOW = "volunteer_edit"
    DELETION_FLOW = "volunteer_deletion"

    def get_active_flow(self, phone: str):
        """
        get_active_flow - Simple wrapper so tests can call flow_manager.get_active_flow().
        """
        return userstate_get_active_flow(phone)

    def start_flow(self, phone: str, flow_name: str):
        """
        start_flow - Begin the specified flow for the user, set initial step.
        """
        if flow_name == self.REGISTRATION_FLOW:
            create_flow(phone, flow_name, start_step="initial")
        elif flow_name == self.EDIT_FLOW:
            create_flow(phone, flow_name, start_step="ask_name")
        elif flow_name == self.DELETION_FLOW:
            create_flow(phone, flow_name, start_step="initial")
        else:
            logger.warning(f"Unknown flow_name={flow_name}; creating with step='start'.")
            create_flow(phone, flow_name, start_step="start")

    def handle_flow_input(self, phone: str, user_input: str) -> str:
        """
        handle_flow_input - Entry point for handling user replies in a multi-step flow.
        """
        flow_name = userstate_get_active_flow(phone)
        if not flow_name:
            return ""

        step = get_flow_step(phone, flow_name)
        user_input_lower = user_input.strip().lower()

        if flow_name == self.REGISTRATION_FLOW:
            return self._handle_registration_flow(phone, step, user_input, user_input_lower)
        elif flow_name == self.EDIT_FLOW:
            return self._handle_edit_flow(phone, step, user_input, user_input_lower)
        elif flow_name == self.DELETION_FLOW:
            return self._handle_deletion_flow(phone, step, user_input, user_input_lower)

        # Unknown flow fallback
        logger.info(f"Unknown flow '{flow_name}' at step '{step}'. Pausing.")
        pause_flow(phone, flow_name)
        return ""

    # --------------------------
    # Registration Flow
    # --------------------------
    def _handle_registration_flow(self, phone: str, step: str, user_input: str, user_input_lower: str) -> str:
        """
        _handle_registration_flow - Guides user through volunteer registration steps.
        """
        record = get_volunteer_record(phone)
        if record:
            # Already registered, bail out
            pause_flow(phone, self.REGISTRATION_FLOW)
            return (
                f"You are already registered as \"{record['name']}\". "
                "Use @bot edit to change your name or @bot delete to remove your profile."
            )

        if step == "initial":
            if not user_input.strip() or user_input_lower == "skip":
                # No name => register Anonymous
                VOLUNTEER_MANAGER.register_volunteer(phone, "Anonymous", [], available=True)
                pause_flow(phone, self.REGISTRATION_FLOW)
                return "Registration completed. You are now 'Anonymous'."
            else:
                # Must have at least two words
                if len(user_input.strip().split()) < 2:
                    return "Please provide your first and last name, or type 'skip' to remain anonymous."
                response = VOLUNTEER_MANAGER.register_volunteer(phone, user_input.strip(), [], available=True)
                pause_flow(phone, self.REGISTRATION_FLOW)
                return response

        # Unknown step => just pause
        pause_flow(phone, self.REGISTRATION_FLOW)
        return ""

    # --------------------------
    # Edit Flow
    # --------------------------
    def _handle_edit_flow(self, phone: str, step: str, user_input: str, user_input_lower: str) -> str:
        """
        _handle_edit_flow - Allows user to change their registered name.
        """
        record = get_volunteer_record(phone)
        if not record:
            # Not registered => start registration flow instead
            pause_flow(phone, self.EDIT_FLOW)
            self.start_flow(phone, self.REGISTRATION_FLOW)
            return (
                "You are not registered, starting registration flow.\n"
                "Please provide your full name or type 'skip' for anonymous."
            )

        if step == "ask_name":
            if user_input_lower == "cancel":
                pause_flow(phone, self.EDIT_FLOW)
                return f"Editing cancelled. You remain \"{record['name']}\"."
            if not user_input.strip() or user_input_lower == "skip":
                pause_flow(phone, self.EDIT_FLOW)
                return f"Editing cancelled. You remain \"{record['name']}\"."

            # Normal name update
            response = VOLUNTEER_MANAGER.register_volunteer(
                phone,
                user_input.strip(),
                [],
                available=record["available"],
                current_role=record["current_role"]
            )
            pause_flow(phone, self.EDIT_FLOW)
            return response

        pause_flow(phone, self.EDIT_FLOW)
        return ""

    # --------------------------
    # Deletion Flow
    # --------------------------
    def _handle_deletion_flow(self, phone: str, step: str, user_input: str, user_input_lower: str) -> str:
        """
        _handle_deletion_flow - Guides user through confirming profile deletion.
        """
        record = get_volunteer_record(phone)
        if not record:
            pause_flow(phone, self.DELETION_FLOW)
            return "You are not currently registered; nothing to delete."

        if step == "initial":
            # user_input_lower in {"yes", "y", "sure"} => proceed to confirm
            if user_input_lower in {"yes", "y", "sure"}:
                set_flow_step(phone, self.DELETION_FLOW, "confirm")
                return "Type 'delete' to confirm removing your profile."
            else:
                pause_flow(phone, self.DELETION_FLOW)
                return "Deletion cancelled."

        if step == "confirm":
            if user_input_lower == "delete":
                confirmation = VOLUNTEER_MANAGER.delete_volunteer(phone)
                pause_flow(phone, self.DELETION_FLOW)
                return confirmation
            else:
                pause_flow(phone, self.DELETION_FLOW)
                return "Deletion cancelled."

        pause_flow(phone, self.DELETION_FLOW)
        return ""

# End of managers/flow_manager.py