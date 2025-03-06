"""
bot.py
------
Python script integrating signal-cli to manage volunteer assignments and process incoming Signal messages.
"""

import subprocess
import re
from typing import Optional, List

# Configuration (update these clearly)
BOT_NUMBER = 'REDACTED_PHONE_NUMBER'

# Volunteer database (temporary simple dict; later move to a database clearly)
VOLUNTEERS = {
    'Jen': {'skills': ['Event Coordination', 'Volunteer Management', 'Logistics Oversight'], 'available': True, 'current_role': None},
    'Daniel': {'skills': ['Public Speaking', 'Press Communication'], 'available': True, 'current_role': None},
    'Julie': {'skills': ['Volunteer Recruitment', 'Event Coordination'], 'available': True, 'current_role': None},
    'Dawn': {'skills': ['Crowd Management', 'Peacekeeping'], 'available': True, 'current_role': None},
    'Austin': {'skills': ['Crowd Management', 'Volunteer Assistance'], 'available': True, 'current_role': None},
    'Raquel': {'skills': ['Greeter'], 'available': True, 'current_role': None},
    'Spence': {'skills': ['Chant Leading'], 'available': True, 'current_role': None},
    'Lynda Young': {'skills': ['General Event Support'], 'available': True, 'current_role': None}
}

# Utilities
def run_signal_cli(args: List[str]) -> subprocess.CompletedProcess:
    """Run signal-cli with provided arguments."""
    full_args = ['signal-cli.bat', '-u', BOT_NUMBER] + args
    # Use UTF-8 encoding and replace decode errors to avoid UnicodeDecodeError.
    result = subprocess.run(full_args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return result

# Message handling
def send_message(to_number: str, message: str):
    """Send a message via signal-cli."""
    run_signal_cli(['send', to_number, '-m', message])
    print(f"Sent to {to_number}: {message}")

def receive_messages() -> List[str]:
    """Retrieve incoming messages via signal-cli."""
    result = run_signal_cli(['receive'])
    if result.stdout is None:
        print("No messages received.")
        return []
    messages = result.stdout.strip().split('\nEnvelope')
    print("Messages received.")
    return messages

# Volunteer management
def find_available_volunteer(skill: str) -> Optional[str]:
    """Find the first available volunteer with a specified skill."""
    for name, data in VOLUNTEERS.items():
        if skill in data['skills'] and data['available'] and data['current_role'] is None:
            return name
    return None

def assign_volunteer(skill: str, role: str) -> Optional[str]:
    """Assign a volunteer with the specified skill to a role."""
    volunteer = find_available_volunteer(skill)
    if volunteer:
        VOLUNTEERS[volunteer]['current_role'] = role
        print(f"Assigned {volunteer} to {role}")
        return volunteer
    print(f"No volunteer available for {role}")
    return None

# Message parsing
def parse_command(message: str) -> Optional[str]:
    """Parse incoming message for commands."""
    assign_match = re.match(r'@bot assign (.+)', message, re.I)
    if assign_match:
        requested_role = assign_match.group(1).strip()
        return requested_role
    return None

def process_incoming():
    """Process incoming messages and respond accordingly."""
    messages = receive_messages()
    for message_text in messages:
        print(f"Processing message:\n{message_text}\n")
        role_requested = parse_command(message_text)
        if role_requested:
            volunteer_assigned = assign_volunteer(role_requested, role_requested)
            response = (f"{role_requested} assigned to {volunteer_assigned}."
                        if volunteer_assigned else
                        f"No available volunteer for {role_requested}.")
            sender_match = re.search(r'from: \??\w+?\?? (\+\d+)', message_text)
            if sender_match:
                sender_number = sender_match.group(1)
                send_message(sender_number, response)

if __name__ == "__main__":
    process_incoming()
