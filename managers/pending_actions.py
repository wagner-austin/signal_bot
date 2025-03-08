"""
managers/pending_actions.py - Encapsulates in-memory pending actions.
Maintains global state for interactive flows (registration, deletion, and event creation).
"""

from typing import Dict, Optional

class PendingActions:
    def __init__(self) -> None:
        self._registrations: Dict[str, str] = {}
        self._deletions: Dict[str, str] = {}
        self._event_creations: Dict[str, bool] = {}  # Pending event creation state

    # Registration methods
    def set_registration(self, sender: str, mode: str) -> None:
        """Sets the pending registration state for a sender."""
        self._registrations[sender] = mode

    def get_registration(self, sender: str) -> Optional[str]:
        """Retrieves the pending registration state for a sender."""
        return self._registrations.get(sender)

    def has_registration(self, sender: str) -> bool:
        """Checks if there is a pending registration state for a sender."""
        return sender in self._registrations

    def clear_registration(self, sender: str) -> None:
        """Clears the pending registration state for a sender."""
        self._registrations.pop(sender, None)

    # Deletion methods
    def set_deletion(self, sender: str, mode: str) -> None:
        """Sets the pending deletion state for a sender."""
        self._deletions[sender] = mode

    def get_deletion(self, sender: str) -> Optional[str]:
        """Retrieves the pending deletion state for a sender."""
        return self._deletions.get(sender)

    def has_deletion(self, sender: str) -> bool:
        """Checks if there is a pending deletion state for a sender."""
        return sender in self._deletions

    def clear_deletion(self, sender: str) -> None:
        """Clears the pending deletion state for a sender."""
        self._deletions.pop(sender, None)

    # Event creation methods
    def set_event_creation(self, sender: str) -> None:
        """Sets the pending event creation state for a sender."""
        self._event_creations[sender] = True

    def has_event_creation(self, sender: str) -> bool:
        """Checks if there is a pending event creation state for a sender."""
        return sender in self._event_creations

    def clear_event_creation(self, sender: str) -> None:
        """Clears the pending event creation state for a sender."""
        self._event_creations.pop(sender, None)

# Global instance for pending actions
PENDING_ACTIONS = PendingActions()

# End of managers/pending_actions.py