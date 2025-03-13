#!/usr/bin/env python
"""
managers/message/pending_handlers.py - Handlers for interactive pending actions.
Handles interactive flows (event creation, deletion, registration) and displays partial usage instructions when input is incomplete.
"""

import logging
from typing import Any, Optional
from managers.message.base_pending_handler import BasePendingHandler
from parsers.message_parser import ParsedMessage
from core.messages import (
    DELETION_CONFIRM_PROMPT, ALREADY_REGISTERED,
    DELETION_PROMPT, EDIT_PROMPT, EDIT_CANCELED, EDIT_CANCELED_WITH_NAME
)
from core.constants import SKIP_VALUES
from core.database import get_volunteer_record
from core.plugin_usage import USAGE_PLAN_EVENT_PARTIAL, USAGE_REGISTER_PARTIAL

logger = logging.getLogger(__name__)

class DeletionPendingHandler(BasePendingHandler):
    """
    DeletionPendingHandler - Handles pending deletion responses.
    """
    def __init__(self, pending_actions: Any, volunteer_manager: Any) -> None:
        super().__init__(pending_actions,
                         pending_actions.has_deletion,
                         pending_actions.get_deletion,
                         pending_actions.clear_deletion)
        self.volunteer_manager: Any = volunteer_manager

    def process_deletion_response(self, parsed: ParsedMessage, sender: str) -> Optional[str]:
        if not self.has_pending(sender):
            return None
        state = self.get_pending(sender)
        user_input = parsed.body.strip().lower() if parsed.body else ""
        if state == "initial":
            if user_input in {"yes", "y", "yea", "sure"}:
                self.pending_actions.set_deletion(sender, "confirm")
                return DELETION_CONFIRM_PROMPT
            else:
                record = get_volunteer_record(sender)
                confirmation = ALREADY_REGISTERED.format(name=record['name']) if record else "Deletion cancelled."
                self.clear_pending(sender)
                return confirmation
        elif state == "confirm":
            if parsed.body.strip() == "DELETE":
                confirmation = self.volunteer_manager.delete_volunteer(sender)
                self.clear_pending(sender)
                return confirmation
            else:
                record = get_volunteer_record(sender)
                confirmation = ALREADY_REGISTERED.format(name=record['name']) if record else "Deletion cancelled."
                self.clear_pending(sender)
                return confirmation
        return None

class RegistrationPendingHandler(BasePendingHandler):
    """
    RegistrationPendingHandler - Handles pending registration and edit responses.
    """
    def __init__(self, pending_actions: Any, volunteer_manager: Any) -> None:
        super().__init__(pending_actions,
                         pending_actions.has_registration,
                         pending_actions.get_registration,
                         pending_actions.clear_registration)
        self.volunteer_manager: Any = volunteer_manager

    def process_registration_response(self, parsed: ParsedMessage, sender: str) -> Optional[str]:
        if not self.has_pending(sender):
            return None
        mode = self.get_pending(sender)
        name_input = parsed.body.strip() if parsed.body else ""
        # If the input seems incomplete (e.g., only one word) and not a skip value, return partial usage prompt.
        if mode in {"register", "edit"} and len(name_input.split()) < 2 and name_input.lower() not in SKIP_VALUES:
            return USAGE_REGISTER_PARTIAL
        if mode == "edit" and name_input.lower() in SKIP_VALUES:
            record = get_volunteer_record(sender)
            confirmation = EDIT_CANCELED_WITH_NAME.format(name=record['name']) if record else EDIT_CANCELED
        elif mode == "register" and name_input.lower() in SKIP_VALUES:
            final_name = "Anonymous"
            confirmation = self.volunteer_manager.register_volunteer(sender, final_name, [])
        else:
            final_name = name_input
            confirmation = self.volunteer_manager.register_volunteer(sender, final_name, [])
        self.clear_pending(sender)
        return confirmation

class EventCreationPendingHandler(BasePendingHandler):
    """
    EventCreationPendingHandler - Handles pending event creation responses.
    """
    def __init__(self, pending_actions: Any) -> None:
        super().__init__(pending_actions,
                         pending_actions.has_event_creation,
                         None,
                         pending_actions.clear_event_creation)

    def process_event_creation_response(self, parsed: ParsedMessage, sender: str) -> Optional[str]:
        from managers.event_manager import create_event
        if not self.has_pending(sender):
            return None
        user_input = parsed.body.strip() if parsed.body else ""
        if user_input.lower() in {"skip", "cancel"}:
            self.clear_pending(sender)
            return "Event creation cancelled."
        try:
            parts = {}
            for part in user_input.split(","):
                if ":" not in part:
                    self.clear_pending(sender)
                    return f"Invalid format. {USAGE_PLAN_EVENT_PARTIAL}"
                key, value = part.split(":", 1)
                parts[key.strip().lower()] = value.strip()
            required_fields = ["title", "date", "time", "location", "description"]
            missing = [field for field in required_fields if field not in parts]
            if missing:
                self.clear_pending(sender)
                return f"Missing fields: {', '.join(missing)}. {USAGE_PLAN_EVENT_PARTIAL}"
            event_id = create_event(
                parts["title"], parts["date"], parts["time"],
                parts["location"], parts["description"]
            )
            self.clear_pending(sender)
            return f"Event '{parts['title']}' created successfully with ID {event_id}."
        except Exception as e:
            logger.exception("Error parsing event details in process_event_creation_response.")
            self.clear_pending(sender)
            return "An internal error occurred while creating the event. Please try again later."

# End of managers/message/pending_handlers.py