#!/usr/bin/env python
"""
managers/user_states_manager.py --- Manager for user state tracking.
Provides functions for tracking multi-step flows and welcome state using a JSON-based flow_state column.
"""

import logging
import json
from core.database.connection import get_connection

logger = logging.getLogger(__name__)

def has_seen_welcome(phone: str) -> bool:
    """
    has_seen_welcome - Checks if the user has already seen the welcome message by inspecting the flow_state JSON.
    
    Args:
        phone (str): The user's phone number.
    
    Returns:
        bool: True if the user has seen the welcome message, else False.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT flow_state FROM UserStates WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    conn.close()
    if row:
        try:
            state = json.loads(row["flow_state"])
            return state.get("has_seen_start", False)
        except Exception:
            return False
    return False

def mark_welcome_seen(phone: str) -> None:
    """
    mark_welcome_seen - Marks the user as having seen the welcome message by updating the flow_state JSON.
    
    Args:
        phone (str): The user's phone number.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT flow_state FROM UserStates WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    if row:
        try:
            state = json.loads(row["flow_state"])
        except Exception:
            state = {}
        state["has_seen_start"] = True
        new_flow_state = json.dumps(state)
        cursor.execute("UPDATE UserStates SET flow_state = ? WHERE phone = ?", (new_flow_state, phone))
    else:
        new_flow_state = json.dumps({"has_seen_start": True})
        cursor.execute("INSERT INTO UserStates (phone, flow_state) VALUES (?, ?)", (phone, new_flow_state))
    conn.commit()
    conn.close()

def set_flow_state(phone: str, flow_name: str) -> None:
    """
    set_flow_state - Sets the current multi-step flow for the user in the flow_state JSON.
    
    Args:
        phone (str): The user's phone number.
        flow_name (str): The name of the flow (e.g., 'registration', 'deletion').
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT flow_state FROM UserStates WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    if row:
        try:
            state = json.loads(row["flow_state"])
        except Exception:
            state = {}
        state["current_flow"] = flow_name
        new_flow_state = json.dumps(state)
        cursor.execute("UPDATE UserStates SET flow_state = ? WHERE phone = ?", (new_flow_state, phone))
    else:
        new_flow_state = json.dumps({"current_flow": flow_name})
        cursor.execute("INSERT INTO UserStates (phone, flow_state) VALUES (?, ?)", (phone, new_flow_state))
    conn.commit()
    conn.close()

def get_flow_state(phone: str) -> str:
    """
    get_flow_state - Retrieves the current multi-step flow for the user from the flow_state JSON.
    
    Args:
        phone (str): The user's phone number.
    
    Returns:
        str: The current flow name (e.g., 'registration') or an empty string if none is set.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT flow_state FROM UserStates WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    conn.close()
    if row:
        try:
            state = json.loads(row["flow_state"])
            return state.get("current_flow", "")
        except Exception:
            return ""
    return ""

def clear_flow_state(phone: str) -> None:
    """
    clear_flow_state - Clears the current multi-step flow for the user by resetting the flow_state JSON.
    
    Args:
        phone (str): The user's phone number.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE UserStates SET flow_state = '{}' WHERE phone = ?", (phone,))
    conn.commit()
    conn.close()

# End of managers/user_states_manager.py