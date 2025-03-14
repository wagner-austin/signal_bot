#!/usr/bin/env python
"""
managers/user_states_manager.py
-------------------------------
Manager for multi-flow user state tracking.
Provides functions to manage multiple flows per user, storing partial data,
and an 'active_flow' for each user.

CHANGES:
 - Replaced single 'flow_state' usage with a 'flows' JSON + 'active_flow'.
 - Provide create_flow, set_flow_step, set_flow_data, pause_flow, resume_flow, etc.
 - Retained legacy logic for backward compatibility, but removed direct references to single flow usage.
"""

import logging
import json
from db.connection import get_connection

logger = logging.getLogger(__name__)

def _get_user_state_row(phone: str):
    """
    Internal helper: Fetch the UserStates row for the given phone, or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT flow_state FROM UserStates WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    conn.close()
    return row

def _save_user_state(phone: str, state_data: dict):
    """
    Internal helper: Saves the entire JSON to flow_state for the user. Creates row if missing.
    """
    conn = get_connection()
    cursor = conn.cursor()
    encoded = json.dumps(state_data)
    # Check if user row exists
    cursor.execute("SELECT phone FROM UserStates WHERE phone = ?", (phone,))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("UPDATE UserStates SET flow_state = ? WHERE phone = ?", (encoded, phone))
    else:
        cursor.execute("INSERT INTO UserStates (phone, flow_state) VALUES (?, ?)", (phone, encoded))
    conn.commit()
    conn.close()

def _load_flows_and_active(phone: str) -> dict:
    """
    Loads the JSON from flow_state, returning a dict with:
      {
        "flows": {
          "<flow_name>": {"step": ..., "data": {...}},
          ...
        },
        "active_flow": "<flow_name or None>"
      }
    If not found, returns an empty structure.
    """
    row = _get_user_state_row(phone)
    if not row:
        return {"flows": {}, "active_flow": None}
    try:
        parsed = json.loads(row["flow_state"])
        if not isinstance(parsed, dict):
            return {"flows": {}, "active_flow": None}
        # Ensure keys exist
        if "flows" not in parsed or not isinstance(parsed["flows"], dict):
            parsed["flows"] = {}
        if "active_flow" not in parsed:
            parsed["active_flow"] = None
        return parsed
    except Exception:
        # Fallback if JSON is corrupted
        return {"flows": {}, "active_flow": None}

def has_seen_welcome(phone: str) -> bool:
    """
    Retained for backward compatibility (legacy usage).
    Checks if user has "has_seen_start" in any existing structure. 
    """
    user_state = _load_flows_and_active(phone)
    # old usage might have stored `{"has_seen_start": true}`
    # We'll check top-level key for legacy data
    return user_state.get("has_seen_start", False)

def mark_welcome_seen(phone: str) -> None:
    """
    Retained for backward compatibility (legacy usage).
    """
    user_state = _load_flows_and_active(phone)
    user_state["has_seen_start"] = True
    _save_user_state(phone, user_state)

#
# New Multi-Flow Functions
#

def create_flow(phone: str, flow_name: str, start_step: str = "start", initial_data: dict = None):
    """
    Create or reset a flow for the user. Then sets it active.
    """
    user_state = _load_flows_and_active(phone)
    user_state["flows"][flow_name] = {
        "step": start_step,
        "data": initial_data if initial_data else {}
    }
    user_state["active_flow"] = flow_name
    _save_user_state(phone, user_state)

def set_flow_step(phone: str, flow_name: str, step: str):
    """
    Update the user's current step in a named flow. 
    Preserves the data. If flow doesn't exist, do nothing.
    """
    user_state = _load_flows_and_active(phone)
    flow = user_state["flows"].get(flow_name)
    if not flow:
        return
    flow["step"] = step
    _save_user_state(phone, user_state)

def set_flow_data(phone: str, flow_name: str, key: str, value):
    """
    Store partial data in the user's flow.
    """
    user_state = _load_flows_and_active(phone)
    flow = user_state["flows"].get(flow_name)
    if not flow:
        return
    flow["data"][key] = value
    _save_user_state(phone, user_state)

def get_flow_data(phone: str, flow_name: str) -> dict:
    """
    Retrieve the data dict for the user's flow. Returns empty if none.
    """
    user_state = _load_flows_and_active(phone)
    return user_state["flows"].get(flow_name, {}).get("data", {})

def get_flow_step(phone: str, flow_name: str) -> str:
    """
    Returns the current step for the user's flow, or empty string if not found.
    """
    user_state = _load_flows_and_active(phone)
    flow = user_state["flows"].get(flow_name)
    if not flow:
        return ""
    return flow.get("step", "")

def pause_flow(phone: str, flow_name: str):
    """
    Pause a flow by removing it as the active_flow if it is currently active.
    """
    user_state = _load_flows_and_active(phone)
    if user_state["active_flow"] == flow_name:
        user_state["active_flow"] = None
        _save_user_state(phone, user_state)

def resume_flow(phone: str, flow_name: str):
    """
    Set the given flow as active_flow if it exists.
    """
    user_state = _load_flows_and_active(phone)
    if flow_name in user_state["flows"]:
        user_state["active_flow"] = flow_name
        _save_user_state(phone, user_state)

def list_flows(phone: str) -> dict:
    """
    Returns a dict of all flows and the user's current step for each.
    Also includes 'active_flow' for convenience.
    """
    user_state = _load_flows_and_active(phone)
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

def get_active_flow(phone: str) -> str:
    """
    Returns the user's currently active flow name, or None if none set.
    """
    user_state = _load_flows_and_active(phone)
    return user_state["active_flow"]

#
# Legacy Single-Flow Compatibility
#

def get_flow_state(phone: str) -> str:
    """
    Legacy: returns an equivalent of a single flow_name. If active_flow is set, return that.
    Otherwise returns "".
    """
    return get_active_flow(phone) or ""

def clear_flow_state(phone: str) -> None:
    """
    Legacy: clear any single flow. We'll just set active_flow=None. 
    """
    user_state = _load_flows_and_active(phone)
    user_state["active_flow"] = None
    _save_user_state(phone, user_state)

# End of managers/user_states_manager.py