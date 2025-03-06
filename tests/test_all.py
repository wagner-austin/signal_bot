"""
tests/test_all.py
-----------------
Integration tests for the Signal bot functionalities.
This module defines tests for message parsing, volunteer assignment, state transitions,
and simulated message sending. It provides a function to run all tests and print a summary.
"""

import asyncio
import logging
from core.state import BotStateMachine
from parsers.message_parser import parse_message
from managers.volunteer_manager import VOLUNTEER_MANAGER

logger = logging.getLogger(__name__)

async def run_tests() -> str:
    results = []
    
    # Test 1: Message Parsing
    try:
        sample_message = (
            "Envelope\n"
            "from: +1234567890\n"
            "Body: @bot test_all\n"
            "Timestamp: 123456789\n"
            "Group info: SomeGroup\n"
            "Message timestamp: 123456789\n"
        )
        parsed = parse_message(sample_message)
        if parsed.sender == "+1234567890" and parsed.body.startswith("@bot"):
            results.append("Message Parsing: PASS")
        else:
            results.append("Message Parsing: FAIL")
    except Exception as e:
        results.append(f"Message Parsing: FAIL ({e})")
    
    # Test 2: Volunteer Assignment
    try:
        volunteer = VOLUNTEER_MANAGER.assign_volunteer("Event Coordination", "Test Role")
        if volunteer:
            results.append("Volunteer Assignment: PASS")
        else:
            results.append("Volunteer Assignment: FAIL (No volunteer assigned)")
    except Exception as e:
        results.append(f"Volunteer Assignment: FAIL ({e})")
    
    # Test 3: State Machine Transition
    try:
        state_machine = BotStateMachine()
        if state_machine.should_continue():
            state_machine.shutdown()
            if not state_machine.should_continue():
                results.append("State Machine Transition: PASS")
            else:
                results.append("State Machine Transition: FAIL (Shutdown did not work)")
        else:
            results.append("State Machine Transition: FAIL (Initial state incorrect)")
    except Exception as e:
        results.append(f"State Machine Transition: FAIL ({e})")
    
    # Test 4: Sending Messages (simulate)
    try:
        # Instead of actually sending a message, we simulate building the command.
        results.append("Send Message: SKIPPED (Simulation)")
    except Exception as e:
        results.append(f"Send Message: FAIL ({e})")
    
    summary = "\n".join(results)
    return summary

def run_all_tests() -> None:
    """
    Run all integration tests and print the summary.
    """
    summary = asyncio.run(run_tests())
    print("Integration Test Summary:\n" + summary)

# End of tests/test_all.py