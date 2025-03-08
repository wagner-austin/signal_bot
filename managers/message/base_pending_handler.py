#!/usr/bin/env python
"""
managers/message/base_pending_handler.py - Base class for pending action handlers.
Provides common utility methods for managing pending actions.
"""

from typing import Any, Callable, Optional

class BasePendingHandler:
    """
    BasePendingHandler - Consolidates common pending state logic.

    Provides methods for checking, retrieving, and clearing pending actions.
    """
    def __init__(self,
                 pending_actions: Any,
                 has_fn: Callable[[str], bool],
                 get_fn: Optional[Callable[[str], Optional[str]]],
                 clear_fn: Callable[[str], None]) -> None:
        """
        Initializes the BasePendingHandler.

        Parameters:
            pending_actions (Any): Global pending actions object.
            has_fn (Callable[[str], bool]): Function to check for a pending state.
            get_fn (Optional[Callable[[str], Optional[str]]]): Function to retrieve the pending state.
            clear_fn (Callable[[str], None]): Function to clear the pending state.
        """
        self.pending_actions: Any = pending_actions
        self.has_fn: Callable[[str], bool] = has_fn
        self.get_fn: Optional[Callable[[str], Optional[str]]] = get_fn
        self.clear_fn: Callable[[str], None] = clear_fn

    def has_pending(self, sender: str) -> bool:
        """Returns True if there is a pending action for the given sender."""
        return self.has_fn(sender)

    def get_pending(self, sender: str) -> Optional[str]:
        """Returns the pending state for the given sender, or None if not set."""
        return self.get_fn(sender) if self.get_fn is not None else None

    def clear_pending(self, sender: str) -> None:
        """Clears the pending action for the given sender."""
        self.clear_fn(sender)

# End of managers/message/base_pending_handler.py