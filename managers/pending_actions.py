"""
managers/pending_actions.py - Encapsulates in-memory pending registration and deletion actions.
Maintains global state for interactive volunteer registration/edit and deletion flows.
Side Effects:
    Methods modify the in-memory state used to track pending actions.
"""

from typing import Dict, Optional

class PendingActions:
    def __init__(self) -> None:
        self._registrations: Dict[str, str] = {}
        self._deletions: Dict[str, str] = {}

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

# Global instance for pending actions
PENDING_ACTIONS = PendingActions()

# End of managers/pending_actions.py