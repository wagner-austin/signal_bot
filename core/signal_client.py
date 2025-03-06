"""
core/signal_client.py
--------------------
Encapsulates functions to interact with signal-cli for sending and receiving messages.
Modified to support replying in group chats if group info is detected.
"""

import subprocess
import re
import time
from core.config import BOT_NUMBER
from managers.message_handler import handle_message

def run_signal_cli(args):
    """Run signal-cli with given arguments."""
    full_args = ['signal-cli.bat', '-u', BOT_NUMBER] + args
    result = subprocess.run(full_args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return result

def send_message(to_number, message, group_id=None):
    """Send a message using signal-cli. If group_id is provided, send to the group chat."""
    if group_id:
        args = ['send', '-g', group_id, '-m', message]
        print(f"Sent to group {group_id}: {message}")
    else:
        args = ['send', to_number, '-m', message]
        print(f"Sent to {to_number}: {message}")
    run_signal_cli(args)

def receive_messages():
    """Retrieve incoming messages using signal-cli."""
    result = run_signal_cli(['receive'])
    if result.stdout:
        messages = result.stdout.strip().split('\nEnvelope')
        return messages
    return []

def process_incoming():
    """
    Process each incoming message, dispatch commands, and send responses.
    Skips system messages (e.g. typing notifications, receipts) which lack a 'Body:'.
    Modified to support replying in group chats when group info is detected.
    """
    messages = receive_messages()
    for message in messages:
        print(f"Processing message:\n{message}\n")

        # Extract sender phone number
        sender_match = re.search(
            r'\s*from:\s*(?:["“]?.+?["”]?\s+)?(\+\d+)',
            message,
            re.IGNORECASE
        )
        sender = sender_match.group(1) if sender_match else None

        # Extract only actual user text (Body:) and skip system/typing messages
        body_match = re.search(r'Body:\s*(.+)', message)
        if not body_match:
            # No 'Body:', so this is likely a system or typing message—skip it
            continue
        body = body_match.group(1).strip()

        # If no recognized sender, skip
        if not sender:
            continue

        # Extract timestamp (in ms)
        timestamp_match = re.search(r'Timestamp:\s*(\d+)', message)
        msg_timestamp = int(timestamp_match.group(1)) if timestamp_match else None

        # --- New: Extract group info if present ---
        group_id = None
        if "Group info:" in message:
            group_id_match = re.search(r'Id:\s*([^\n]+)', message)
            if group_id_match:
                group_id = group_id_match.group(1).strip()

        # Pass the real message text to our message handler
        response = handle_message(body, sender, msg_timestamp=msg_timestamp)
        if response:
            send_message(sender, response, group_id=group_id)
