#!/usr/bin/env python
"""
managers/message/pending_handlers.py
------------------------------------
Handlers for interactive pending actions: deletion, registration, and event creation.
They use the global PendingActions state, which is concurrency-safe.
Now includes a note on concurrency: multiple users may concurrently plan events,
delete registrations, or register with partial inputs. The logic here is designed to
handle concurrency via the thread-safe PendingActions structure.
"""

import logging
from typing import Any, Optional
from managers.message.base_pending_handler import BasePendingHandler
from parsers.message_parser import ParsedMessage
from core.messages import (
    DELETION_CONFIRM_PROMPT, ALREADY_REGISTERED,
    DELETION_CANCELED, EDIT_PROMPT, EDIT_CANCELED, EDIT_CANCELED_WITH_NAME
)
from core.constants import SKIP_VALUES

logger = logging.getLogger(__name__)

class DeletionPendingHandler(BasePendingHandler):
    """
    DeletionPendingHandler - Handles pending deletion responses.

    Concurrency:
        Multiple threads or users can concurrently set or clear deletion states in PendingActions.
        This handler checks the existing state carefully before proceeding.
    """
    def __init__(self, pending_actions: Any, volunteer_manager: Any) -> None:
        super().__init__(pending_actions,
                         pending_actions.has_deletion,
                         pending_actions.get_deletion,
                         pending_actions.clear_deletion)
        self.volunteer_manager: Any = volunteer_manager

    def process_deletion_response(self, parsed: ParsedMessage, sender: str) -> Optional[str]:
        """
        Processes deletion response from a volunteer.

        Returns:
            Optional[str]: Response message or None.
        """
        if not self.has_pending(sender):
            return None
        state = self.get_pending(sender)
        user_input = parsed.body.strip().lower() if parsed.body else ""
        if state == "initial":
            if user_input in {"yes", "y", "yea", "sure"}:
                self.pending_actions.set_deletion(sender, "confirm")
                return DELETION_CONFIRM_PROMPT
            else:
                from core.database import get_volunteer_record
                record = get_volunteer_record(sender)
                confirmation = ALREADY_REGISTERED.format(name=record['name']) if record else DELETION_CANCELED
                self.clear_pending(sender)
                return confirmation
        elif state == "confirm":
            if parsed.body.strip() == "DELETE":
                confirmation = self.volunteer_manager.delete_volunteer(sender)
                self.clear_pending(sender)
                return confirmation
            else:
                from core.database import get_volunteer_record
                record = get_volunteer_record(sender)
                confirmation = ALREADY_REGISTERED.format(name=record['name']) if record else DELETION_CANCELED
                self.clear_pending(sender)
                return confirmation
        return None


class RegistrationPendingHandler(BasePendingHandler):
    """
    RegistrationPendingHandler - Handles pending registration and edit responses.

    Concurrency:
        Multiple users can concurrently initiate or edit registrations.
        The underlying PendingActions ensures thread-safe state transitions.
    """
    def __init__(self, pending_actions: Any, volunteer_manager: Any) -> None:
        super().__init__(pending_actions,
                         pending_actions.has_registration,
                         pending_actions.get_registration,
                         pending_actions.clear_registration)
        self.volunteer_manager: Any = volunteer_manager

    def process_registration_response(self, parsed: ParsedMessage, sender: str) -> Optional[str]:
        """
        Processes registration or edit response from a volunteer.

        Returns:
            Optional[str]: Response message or None.
        """
        if not self.has_pending(sender):
            return None
        mode = self.get_pending(sender)
        name_input = parsed.body.strip() if parsed.body else ""
        if mode == "edit" and name_input.lower() in SKIP_VALUES:
            from core.database import get_volunteer_record
            record = get_volunteer_record(sender)
            confirmation = EDIT_CANCELED_WITH_NAME.format(name=record['name']) if record else EDIT_CANCELED
        elif mode == "register" and name_input.lower() in SKIP_VALUES:
            final_name = "Anonymous"
            confirmation = self.volunteer_manager.sign_up(sender, final_name, [])
        else:
            final_name = name_input
            confirmation = self.volunteer_manager.sign_up(sender, final_name, [])
        self.clear_pending(sender)
        return confirmation


class EventCreationPendingHandler(BasePendingHandler):
    """
    EventCreationPendingHandler - Handles pending event creation responses.

    Concurrency:
        Multiple users can concurrently call event creation. The pending actions
        for each sender are distinct, preventing data overlap. However, partial
        or invalid inputs from many users at once should be handled gracefully.
    """
    def __init__(self, pending_actions: Any) -> None:
        super().__init__(pending_actions,
                         pending_actions.has_event_creation,
                         None,
                         pending_actions.clear_event_creation)

    def process_event_creation_response(self, parsed: ParsedMessage, sender: str) -> Optional[str]:
        """
        Processes event creation response from a volunteer.

        Returns:
            Optional[str]: Confirmation or cancellation message.
        """
        from core.event_manager import create_event
        if not self.has_pending(sender):
            return None
        user_input = parsed.body.strip() if parsed.body else ""
        if user_input.lower() in {"skip", "cancel"}:
            self.clear_pending(sender)
            return "Event creation cancelled."
        try:
            parts = {}
            for part in user_input.split(","):
                key, value = part.split(":", 1)
                parts[key.strip().lower()] = value.strip()
            required_fields = ["title", "date", "time", "location", "description"]
            if not all(field in parts for field in required_fields):
                self.clear_pending(sender)
                return "Missing one or more required fields. Event creation cancelled."
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