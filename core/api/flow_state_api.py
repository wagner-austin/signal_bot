#!/usr/bin/env python
"""
core/api/flow_state_api.py
--------------------------
Stable façade for multi-step flows. Delegates all flow operations to the centralized FlowManager.
"""

import logging
from typing import Optional, Dict

from managers.flow_manager import FlowManager

logger = logging.getLogger(__name__)
_flow_manager = FlowManager()

def start_flow(phone: str, flow_name: str) -> None:
    """
    Begin or reset the specified flow for the user by delegating to FlowManager.
    """
    _flow_manager.start_flow(phone, flow_name)

def pause_flow(phone: str, flow_name: str) -> None:
    """
    Pause the specified flow for the user by delegating to FlowManager.
    """
    _flow_manager.pause_flow(phone, flow_name)

def resume_flow(phone: str, flow_name: str) -> None:
    """
    Resume a previously paused flow for the user by delegating to FlowManager.
    """
    _flow_manager.resume_flow(phone, flow_name)

def get_active_flow(phone: str) -> Optional[str]:
    """
    Return the name of the active flow for the user, or None if none, by delegating to FlowManager.
    """
    return _flow_manager.get_active_flow(phone)

def handle_flow_input(phone: str, user_input: str) -> str:
    """
    Process a piece of user input in the active flow (if any) by delegating to FlowManager.
    Returns any user-facing response message.
    """
    return _flow_manager.handle_flow_input(phone, user_input)

def list_flows(phone: str) -> dict:
    """
    Return a dictionary containing the active flow and all flows for the user,
    by delegating to FlowManager.
    """
    return _flow_manager.list_flows(phone)

# End of core/api/flow_state_api.py