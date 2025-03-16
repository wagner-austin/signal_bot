"""
managers/user_states_manager.py
-------------------------------
Manager for multi-flow user state tracking and persistence.
Now uses core.api.db_api for DB access, but keeps advanced domain logic in place.
"""

import logging
import json
from typing import Dict, Any
from core.api import db_api

logger = logging.getLogger(__name__)

def _get_user_state_row(phone: str):
    """
    Internal helper to retrieve the user's state row from the DB.
    Returns a dict or None.
    """
    query = "SELECT phone, flow_state FROM UserStates WHERE phone = ?"
    return db_api.fetch_one(query, (phone,))

def _save_user_state(phone: str, state_data: dict):
    """
    Internal helper to insert or update the user's state row in the DB.
    """
    encoded = json.dumps(state_data)
    existing = _get_user_state_row(phone)
    if existing:
        query = "UPDATE UserStates SET flow_state = ? WHERE phone = ?"
        db_api.execute_query(query, (encoded, phone), commit=True)
    else:
        data = {"phone": phone, "flow_state": encoded}
        db_api.insert_record("UserStates", data)

def _load_flows_and_active(phone: str) -> dict:
    """
    Internal utility to parse the user's flow_state JSON into a dict.
    """
    row = _get_user_state_row(phone)
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

def has_seen_welcome(phone: str) -> bool:
    user_state = _load_flows_and_active(phone)
    return user_state.get("has_seen_start", False)

def mark_welcome_seen(phone: str) -> None:
    user_state = _load_flows_and_active(phone)
    user_state["has_seen_start"] = True
    _save_user_state(phone, user_state)

def create_flow(phone: str, flow_name: str, start_step: str = "start", initial_data: dict = None):
    user_state = _load_flows_and_active(phone)
    user_state["flows"][flow_name] = {
        "step": start_step,
        "data": initial_data if initial_data else {}
    }
    user_state["active_flow"] = flow_name
    _save_user_state(phone, user_state)

def set_flow_step(phone: str, flow_name: str, step: str):
    user_state = _load_flows_and_active(phone)
    flow = user_state["flows"].get(flow_name)
    if not flow:
        return
    flow["step"] = step
    _save_user_state(phone, user_state)

def get_flow_step(phone: str, flow_name: str) -> str:
    user_state = _load_flows_and_active(phone)
    flow = user_state["flows"].get(flow_name)
    if not flow:
        return ""
    return flow.get("step", "")

def pause_flow(phone: str, flow_name: str):
    user_state = _load_flows_and_active(phone)
    if user_state["active_flow"] == flow_name:
        user_state["active_flow"] = None
        _save_user_state(phone, user_state)

def resume_flow(phone: str, flow_name: str):
    user_state = _load_flows_and_active(phone)
    if flow_name in user_state["flows"]:
        user_state["active_flow"] = flow_name
        _save_user_state(phone, user_state)

def list_flows(phone: str) -> dict:
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
    user_state = _load_flows_and_active(phone)
    return user_state["active_flow"]

def clear_flow_state(phone: str) -> None:
    user_state = _load_flows_and_active(phone)
    user_state["active_flow"] = None
    _save_user_state(phone, user_state)

# End of managers/user_states_manager.py