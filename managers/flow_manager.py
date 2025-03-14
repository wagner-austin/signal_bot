#!/usr/bin/env python
"""
managers/flow_manager.py - Centralized flow management for multi-step volunteer flows.
This module orchestrates all multi-step volunteer flows using a unified approach via FlowManager and user_states_manager.
"""

import logging
from managers.user_states_manager import (
    get_active_flow,
    create_flow,
    pause_flow,
    set_flow_step,
    get_flow_step,
    resume_flow
)
from managers.volunteer_manager import VOLUNTEER_MANAGER
from db.volunteers import get_volunteer_record
from core.plugin_usage import USAGE_REGISTER_PARTIAL  # Added for validation prompt

logger = logging.getLogger(__name__)

class FlowManager:
    """
    FlowManager - Orchestrates all multi-step volunteer flows in a unified way.
    Exposes methods to start a flow and handle user input for each step.
    """

    REGISTRATION_FLOW = "volunteer_registration"
    EDIT_FLOW = "volunteer_edit"
    DELETION_FLOW = "volunteer_deletion"

    def start_flow(self, phone: str, flow_name: str):
        """
        start_flow - Begin the specified flow for the user, setting the initial step.
        If the flow_name is unknown, create a "generic" flow with step="start".
        """
        if flow_name == self.REGISTRATION_FLOW:
            create_flow(phone, flow_name, start_step="initial")
        elif flow_name == self.EDIT_FLOW:
            create_flow(phone, flow_name, start_step="ask_name")
        elif flow_name == self.DELETION_FLOW:
            create_flow(phone, flow_name, start_step="initial")
        else:
            logger.warning(f"Unknown flow_name={flow_name} used in start_flow, creating anyway with step='start'.")
            create_flow(phone, flow_name, start_step="start")

    def handle_flow_input(self, phone: str, user_input: str) -> str:
        """
        handle_flow_input - Central point to handle user replies while in a flow.
        Looks up the user's active flow, current step, and processes logic accordingly.
        """
        flow_name = get_active_flow(phone)
        if not flow_name:
            return ""  # No active flow, do nothing

        step = get_flow_step(phone, flow_name)
        user_input_lower = user_input.strip().lower()

        if flow_name == self.REGISTRATION_FLOW:
            return self._handle_registration_flow(phone, step, user_input, user_input_lower)

        if flow_name == self.EDIT_FLOW:
            return self._handle_edit_flow(phone, step, user_input, user_input_lower)

        if flow_name == self.DELETION_FLOW:
            return self._handle_deletion_flow(phone, step, user_input, user_input_lower)

        # For unknown flows, pause and return an empty response.
        logger.info(f"Received input for unknown flow '{flow_name}', step '{step}' => returning empty string.")
        pause_flow(phone, flow_name)
        return ""

    # ---------------------------
    # Registration Flow
    # ---------------------------
    def _handle_registration_flow(self, phone: str, step: str,
                                  user_input: str, user_input_lower: str) -> str:
        """
        _handle_registration_flow - Handles the volunteer registration flow.
        Steps: 'initial' => registration completion.
        Validates that a full name (first and last) is provided unless skipped.
        """
        existing = get_volunteer_record(phone)
        if existing:
            pause_flow(phone, self.REGISTRATION_FLOW)
            return (f"You are registered as \"{existing['name']}\".\n"
                    "Use @bot edit to change your name or @bot delete to remove your profile.")

        if step == "initial":
            if not user_input.strip() or user_input_lower == "skip":
                VOLUNTEER_MANAGER.register_volunteer(phone, "skip", [])
                pause_flow(phone, self.REGISTRATION_FLOW)
                return "You have been registered as Anonymous."
            else:
                # Enforce full name requirement: must be at least two words.
                if len(user_input.strip().split()) < 2:
                    return USAGE_REGISTER_PARTIAL
                response = VOLUNTEER_MANAGER.register_volunteer(phone, user_input.strip(), [])
                pause_flow(phone, self.REGISTRATION_FLOW)
                return response

        pause_flow(phone, self.REGISTRATION_FLOW)
        return ""

    # ---------------------------
    # Edit Flow
    # ---------------------------
    def _handle_edit_flow(self, phone: str, step: str,
                          user_input: str, user_input_lower: str) -> str:
        """
        _handle_edit_flow - Handles the volunteer edit flow.
        Steps: 'ask_name' => update registration.
        """
        from db.volunteers import get_volunteer_record
        record = get_volunteer_record(phone)
        if not record:
            pause_flow(phone, self.EDIT_FLOW)
            self.start_flow(phone, self.REGISTRATION_FLOW)
            return ("You are not registered, starting registration flow.\n"
                    "Please provide your full name or type 'skip' to remain anonymous.")

        if step == "ask_name":
            if user_input_lower == "cancel":
                pause_flow(phone, self.EDIT_FLOW)
                return "Editing cancelled."
            if not user_input.strip() or user_input_lower == "skip":
                pause_flow(phone, self.EDIT_FLOW)
                return f"Editing cancelled. You remain registered as \"{record['name']}\"."
            response = VOLUNTEER_MANAGER.register_volunteer(phone, user_input.strip(), [])
            pause_flow(phone, self.EDIT_FLOW)
            return response

        pause_flow(phone, self.EDIT_FLOW)
        return ""

    # ---------------------------
    # Deletion Flow
    # ---------------------------
    def _handle_deletion_flow(self, phone: str, step: str,
                              user_input: str, user_input_lower: str) -> str:
        """
        _handle_deletion_flow - Handles the volunteer deletion flow.
        Steps: 'initial' => 'confirm' => deletion completion.
        """
        from db.volunteers import get_volunteer_record
        record = get_volunteer_record(phone)
        if not record:
            pause_flow(phone, self.DELETION_FLOW)
            return "You are not currently registered; nothing to delete."

        if step == "initial":
            if user_input_lower in {"yes", "y", "sure"}:
                set_flow_step(phone, self.DELETION_FLOW, "confirm")
                return "Are you sure you want to delete your profile? Type 'delete' to confirm."
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