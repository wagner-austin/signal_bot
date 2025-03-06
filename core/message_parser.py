"""
core/message_parser.py
----------------------
Module for parsing incoming messages using regex extraction.
Centralizes common regex patterns for consistency.
"""

import re
from typing import Optional, Dict, Any

# Define common regex patterns as constants
SENDER_PATTERN: str = r'\s*from:\s*(?:["“]?.+?["”]?\s+)?(\+\d+)'
BODY_PATTERN: str = r'Body:\s*(.+)'
TIMESTAMP_PATTERN: str = r'Timestamp:\s*(\d+)'
GROUP_INFO_PATTERN: str = r'Id:\s*([^\n]+)'

def parse_sender(message: str) -> Optional[str]:
    """
    Extract and return the sender phone number from the message.
    
    Args:
        message (str): The incoming message string.
        
    Returns:
        Optional[str]: The sender's phone number if found, otherwise None.
    """
    match = re.search(SENDER_PATTERN, message, re.IGNORECASE)
    return match.group(1) if match else None

def parse_body(message: str) -> Optional[str]:
    """
    Extract and return the message body.
    
    Args:
        message (str): The incoming message string.
        
    Returns:
        Optional[str]: The message body if found, otherwise None.
    """
    match = re.search(BODY_PATTERN, message)
    return match.group(1).strip() if match else None

def parse_timestamp(message: str) -> Optional[int]:
    """
    Extract and return the message timestamp as an integer.
    
    Args:
        message (str): The incoming message string.
        
    Returns:
        Optional[int]: The message timestamp if found, otherwise None.
    """
    match = re.search(TIMESTAMP_PATTERN, message)
    return int(match.group(1)) if match else None

def parse_group_info(message: str) -> Optional[str]:
    """
    Extract and return the group ID if available.
    
    Args:
        message (str): The incoming message string.
        
    Returns:
        Optional[str]: The group ID if found, otherwise None.
    """
    if "Group info:" in message:
        match = re.search(GROUP_INFO_PATTERN, message)
        return match.group(1).strip() if match else None
    return None

def parse_message(message: str) -> Dict[str, Optional[Any]]:
    """
    Parse the incoming message and return a dictionary with details.
    
    Args:
        message (str): The full incoming message text.
        
    Returns:
        Dict[str, Optional[Any]]: A dictionary containing:
            - 'sender': The sender's phone number (str) or None.
            - 'body': The text body of the message (str) or None.
            - 'timestamp': The message timestamp (int) or None.
            - 'group_id': The group ID (str) if from a group, else None.
    """
    return {
        'sender': parse_sender(message),
        'body': parse_body(message),
        'timestamp': parse_timestamp(message),
        'group_id': parse_group_info(message)
    }

# End of core/message_parser.py