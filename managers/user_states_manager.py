#!/usr/bin/env python
"""
managers/user_states_manager.py - Manager for user state tracking.
Provides functions for checking and updating whether a user (phone number) has seen the welcome message.
"""

import logging
from core.database.connection import get_connection

logger = logging.getLogger(__name__)

def has_seen_welcome(phone: str) -> bool:
    """
    has_seen_welcome - Checks if the user has already seen the welcome message.
    
    Args:
        phone (str): The user's phone number.
    
    Returns:
        bool: True if has_seen_start is 1; otherwise, False.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT has_seen_start FROM UserStates WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row["has_seen_start"] == 1
    return False

def mark_welcome_seen(phone: str) -> None:
    """
    mark_welcome_seen - Marks the user as having seen the welcome message.
    
    Args:
        phone (str): The user's phone number.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT phone FROM UserStates WHERE phone = ?", (phone,))
    if cursor.fetchone():
        cursor.execute("UPDATE UserStates SET has_seen_start = 1 WHERE phone = ?", (phone,))
    else:
        cursor.execute("INSERT INTO UserStates (phone, has_seen_start) VALUES (?, 1)", (phone,))
    conn.commit()
    conn.close()

# End of managers/user_states_manager.py