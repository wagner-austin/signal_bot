#!/usr/bin/env python
"""
managers/flow_manager.py
------------------------
Consolidated domain logic for multi-step volunteer flows and user states.
All flow and user state management is now centralized here, including welcome state.
"""

import logging
import json
from typing import Optional, Dict

from db.volunteers import get_volunteer_record
from managers.volunteer_manager import VOLUNTEER_MANAGER
from plugins import messages
from core.api import db_api

logger = logging.getLogger(__name__)

# Flow Identifiers
REGISTRATION_FLOW = "volunteer_registration"
EDIT_FLOW = "volunteer_edit"
DELETION_FLOW = "volunteer_deletion"

class FlowManager:
    """
    FlowManager - Encapsulates domain logic for multi-step volunteer flows
    and user state tracking (including welcome-seen status).
    Exposes methods:
      - start_flow, pause_flow, resume_flow
      - get_active_flow, handle_flow_input, list_flows
      - has_seen_welcome, mark_welcome_seen
    All state operations are centralized here.
    """

    # --------------------------------------------------------
    # Public Flow Lifecycle Methods
    # --------------------------------------------------------
    def start_flow(self, phone: str, flow_name: str):
        """
        Begin or reset the specified flow for the user, setting initial flow state.
        """
        self._create_flow(phone, flow_name)

    def pause_flow(self, phone: str, flow_name: str):
        """
        Temporarily pause the specified flow for the user.
        """
        self._pause_flow_state(phone, flow_name)

    def resume_flow(self, phone: str, flow_name: str):
        """
        Resume a previously paused flow for the user.
        """
        self._resume_flow_state(phone, flow_name)

    def get_active_flow(self, phone: str) -> Optional[str]:
        """
        Return the name of the flow the user is currently in, or None if none.
        """
        return self._get_active_flow_state(phone)

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

    def list_flows(self, phone: str) -> dict:
        """
        Return a dictionary with "active_flow" and "flows" from the user state.
        """
        user_state = self._load_flows_and_active(phone)
        results = {}
        for flow_name, flow_info in user_state["flows"].items():
            results[flow_name] = {
                "step": flow_info.get("step"),
                "data_count": len(flow_info.get("data", {}))
            }
        return {
            "active_flow": user_state["active_flow"],
            "flows": results
        }

    # --------------------------------------------------------
    # Public Welcome-Tracking Methods
    # --------------------------------------------------------
    def has_seen_welcome(self, phone: str) -> bool:
        """
        Return True if the user has previously seen the welcome message, otherwise False.
        """
        user_state = self._load_flows_and_active(phone)
        return user_state.get("has_seen_start", False)

    def mark_welcome_seen(self, phone: str) -> None:
        """
        Record that the user has now seen the welcome message.
        """
        user_state = self._load_flows_and_active(phone)
        user_state["has_seen_start"] = True
        self._save_user_state(phone, user_state)

    # --------------------------------------------------------
    # Internal Flow Handlers
    # --------------------------------------------------------
    def _handle_registration_flow(self, phone: str, user_input: str) -> str:
        """
        Handle input for the multi-step volunteer registration flow.
        If the user is already registered, return an 'already registered' message.
        If input is empty, return the 'registration welcome' prompt.
        If input is 'skip', register as Anonymous.
        If the name is too short (<2 words), re-prompt by returning the welcome again.
        Otherwise, register with the provided name.
        """
        record = get_volunteer_record(phone)
        if record:
            self.pause_flow(phone, REGISTRATION_FLOW)
            return messages.ALREADY_REGISTERED_WITH_INSTRUCTIONS.format(name=record["name"])

        stripped_input = user_input.strip()
        if not stripped_input:
            # Prompt user for name
            return messages.REGISTRATION_WELCOME

        lower_input = stripped_input.lower()
        if lower_input == "skip":
            VOLUNTEER_MANAGER.register_volunteer(phone, "Anonymous", available=True)
            self.pause_flow(phone, REGISTRATION_FLOW)
            return messages.REGISTRATION_COMPLETED_ANONYMOUS

        # If user gave something but too short (less than 2 words), ask again
        if len(stripped_input.split()) < 2:
            return messages.REGISTRATION_WELCOME

        # Final: register with provided name
        response = VOLUNTEER_MANAGER.register_volunteer(phone, stripped_input, available=True)
        self.pause_flow(phone, REGISTRATION_FLOW)
        return response

    def _handle_edit_flow(self, phone: str, user_input: str) -> str:
        """
        Handle input for the multi-step edit flow.
        If user is not registered, pivot to registration flow.
        If user_input is empty, show the edit prompt.
        If user_input is cancel/skip, pause the flow with a message.
        Otherwise, update the name and pause the flow.
        """
        record = get_volunteer_record(phone)
        if not record:
            self.pause_flow(phone, EDIT_FLOW)
            self.start_flow(phone, REGISTRATION_FLOW)
            return messages.EDIT_NOT_REGISTERED

        stripped = user_input.strip()
        user_input_lower = stripped.lower()

        if not user_input_lower:
            # Prompt user for new name
            return messages.EDIT_PROMPT

        if user_input_lower in ["cancel", "skip"]:
            self.pause_flow(phone, EDIT_FLOW)
            return messages.EDIT_CANCELED_WITH_NAME.format(name=record["name"])

        # Normal name update
        response = VOLUNTEER_MANAGER.register_volunteer(
            phone,
            stripped,
            available=record["available"]
        )
        self.pause_flow(phone, EDIT_FLOW)
        return response

    def _handle_deletion_flow(self, phone: str, user_input: str) -> str:
        """
        Handle input for the multi-step deletion flow.
        If user not found, pause flow & inform user there's nothing to delete.
        On the 'start' step, if user input is empty, prompt for confirmation.
        If user says 'yes' or 'y' or 'sure', go to 'confirm' step.
        If user says anything else, cancel deletion.
        On the 'confirm' step, if user says 'delete', perform deletion.
        Otherwise, cancel deletion.
        """
        record = get_volunteer_record(phone)
        if not record:
            self.pause_flow(phone, DELETION_FLOW)
            return messages.NOTHING_TO_DELETE

        step_input = user_input.strip().lower()
        current_step = self._get_flow_step(phone, DELETION_FLOW) or "start"

        if current_step == "start":
            # If user input is empty, prompt them
            if not step_input:
                return messages.DELETION_PROMPT
            if step_input in {"yes", "y", "sure"}:
                self._set_flow_step(phone, DELETION_FLOW, "confirm")
                return messages.DELETION_CONFIRM_PROFILE
            else:
                self.pause_flow(phone, DELETION_FLOW)
                return messages.DELETION_CANCELED

        elif current_step == "confirm":
            if step_input == "delete":
                VOLUNTEER_MANAGER.delete_volunteer(phone)
                self.pause_flow(phone, DELETION_FLOW)
                return messages.VOLUNTEER_DELETED
            else:
                self.pause_flow(phone, DELETION_FLOW)
                return messages.DELETION_CANCELED

        self.pause_flow(phone, DELETION_FLOW)
        return ""

    # --------------------------------------------------------
    # Private Wrapper Methods for Flow State
    # --------------------------------------------------------
    def _create_flow(self, phone: str, flow_name: str, start_step: str = "start", initial_data: dict = None):
        """
        Create or reset a flow in the user's state and make it active.
        """
        user_state = self._load_flows_and_active(phone)
        user_state["flows"][flow_name] = {
            "step": start_step,
            "data": initial_data if initial_data else {}
        }
        user_state["active_flow"] = flow_name
        self._save_user_state(phone, user_state)

    def _pause_flow_state(self, phone: str, flow_name: str):
        user_state = self._load_flows_and_active(phone)
        if user_state["active_flow"] == flow_name:
            user_state["active_flow"] = None
            self._save_user_state(phone, user_state)

    def _resume_flow_state(self, phone: str, flow_name: str):
        user_state = self._load_flows_and_active(phone)
        if flow_name in user_state["flows"]:
            user_state["active_flow"] = flow_name
            self._save_user_state(phone, user_state)

    def _get_active_flow_state(self, phone: str) -> Optional[str]:
        user_state = self._load_flows_and_active(phone)
        return user_state["active_flow"]

    def _get_flow_step(self, phone: str, flow_name: str) -> str:
        user_state = self._load_flows_and_active(phone)
        flow = user_state["flows"].get(flow_name)
        if not flow:
            return ""
        return flow.get("step", "")

    def _set_flow_step(self, phone: str, flow_name: str, step: str):
        user_state = self._load_flows_and_active(phone)
        flow = user_state["flows"].get(flow_name)
        if not flow:
            return
        flow["step"] = step
        self._save_user_state(phone, user_state)

    # --------------------------------------------------------
    # Private User State Persistence
    # --------------------------------------------------------
    def _get_user_state_row(self, phone: str) -> Optional[Dict[str, any]]:
        """
        Internal helper to retrieve the user's state row from the DB.
        Returns a dict or None.
        """
        query = "SELECT phone, flow_state FROM UserStates WHERE phone = ?"
        return db_api.fetch_one(query, (phone,))

    def _save_user_state(self, phone: str, state_data: dict) -> None:
        """
        Insert or update the user's state row in the DB.
        """
        encoded = json.dumps(state_data)
        existing = self._get_user_state_row(phone)
        if existing:
            query = "UPDATE UserStates SET flow_state = ? WHERE phone = ?"
            db_api.execute_query(query, (encoded, phone), commit=True)
        else:
            data = {"phone": phone, "flow_state": encoded}
            db_api.insert_record("UserStates", data)

    def _load_flows_and_active(self, phone: str) -> dict:
        """
        Parse the user's flow_state JSON into a dict with:
          { "flows": {...}, "active_flow": None or <flow_name> }
        """
        row = self._get_user_state_row(phone)
        if not row:
            return {"flows": {}, "active_flow": None}
        try:
            parsed = json.loads(row["flow_state"])
            if not isinstance(parsed, dict):
                return {"flows": {}, "active_flow": None}
            if "flows" not in parsed or not isinstance(parsed["flows"], dict):
                parsed["flows"] = {}
            if "active_flow" not in parsed:
                parsed["active_flow"] = None
            return parsed
        except Exception:
            return {"flows": {}, "active_flow": None}

# End of managers/flow_manager.py