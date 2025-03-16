# File: core/api/flow_state_api.py
"""
core/api/flow_state_api.py
--------------------------
A stable façade for multi-step flows.
Provides start/pause/resume/get/handle_flow_input methods that delegate to FlowManager,
and now also provides a list_flows method for reading all flows.

Usage:
   (Not a plugin; used by plugins and managers for flow operations.)
"""

import logging
from typing import Optional, Dict

from managers.flow_manager import FlowManager

logger = logging.getLogger(__name__)

_flow_manager = FlowManager()

def start_flow(phone: str, flow_name: str) -> None:
    """
    Begin or reset the specified flow for the user, using FlowManager.
    """
    _flow_manager.start_flow(phone, flow_name)

def pause_flow(phone: str, flow_name: str) -> None:
    """
    Pause the specified flow for the user.
    """
    _flow_manager.pause_flow(phone, flow_name)

def resume_flow(phone: str, flow_name: str) -> None:
    """
    Resume a previously paused flow for the user.
    """
    _flow_manager.resume_flow(phone, flow_name)

def get_active_flow(phone: str) -> Optional[str]:
    """
    Return the name of the flow the user is currently in, or None if none.
    """
    return _flow_manager.get_active_flow(phone)

def handle_flow_input(phone: str, user_input: str) -> str:
    """
    Process a piece of user input in the currently active flow (if any).
    Dispatches to domain-specific handlers in FlowManager.
    Returns any user-facing response message.
    """
    return _flow_manager.handle_flow_input(phone, user_input)

def list_flows(phone: str) -> dict:
    """
    Return all flows for the user, including the active flow, by calling FlowManager.
    """
    return _flow_manager.list_flows(phone)

# End of core/api/flow_state_api.py