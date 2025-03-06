"""
tests/test_all.py
-----------------
Integration tests for the Signal bot functionalities.
This module defines tests for message parsing, volunteer assignment, state transitions,
direct/indirect message sending, command execution, and invalid command handling.
It provides a function to run all tests and print a summary.
"""

import asyncio
import logging
from core.state import BotStateMachine
from parsers.message_parser import parse_message, ParsedMessage
from managers.volunteer_manager import VOLUNTEER_MANAGER
from plugins.commands import assign_command, test_command, shutdown_command, test_all_command
from managers.message_handler import handle_message
import core.signal_client as sc

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
    
    # Test 2: Command 'assign'
    try:
        # Call assign_command with a valid skill.
        response = assign_command("Event Coordination", "+111", BotStateMachine())
        if "assigned to" in response or "No available volunteer" in response:
            results.append("Command 'assign': PASS")
        else:
            results.append("Command 'assign': FAIL")
    except Exception as e:
        results.append(f"Command 'assign': FAIL ({e})")
    
    # Test 3: Command 'test'
    try:
        response = test_command("", "+111", BotStateMachine())
        if response.strip() == "yes":
            results.append("Command 'test': PASS")
        else:
            results.append("Command 'test': FAIL")
    except Exception as e:
        results.append(f"Command 'test': FAIL ({e})")
    
    # Test 4: Command 'shutdown'
    try:
        state_machine = BotStateMachine()
        response = shutdown_command("", "+111", state_machine)
        if response.strip() == "Bot is shutting down." and not state_machine.should_continue():
            results.append("Command 'shutdown': PASS")
        else:
            results.append("Command 'shutdown': FAIL")
    except Exception as e:
        results.append(f"Command 'shutdown': FAIL ({e})")
    
    # Test 5: Direct reply in group chat (simulate send_message)
    try:
        # Patch the async_run_signal_cli in core.signal_client
        original_async_run = sc.async_run_signal_cli
        calls = []
        async def dummy_async_run(args):
            calls.append(args)
            return "dummy output"
        sc.async_run_signal_cli = dummy_async_run
        
        # Call send_message as if in a group chat with reply quoting.
        await sc.send_message(
            to_number="+111",
            message="Group message",
            group_id="dummyGroupBase64",  # dummy valid base64 string substitute
            reply_quote_author="+222",
            reply_quote_timestamp="123",
            reply_quote_message="original"
        )
        # Verify that the arguments include group flags and reply quoting flags.
        args_str = " ".join(calls[0])
        if "-g" in args_str and "--quote-author" in args_str:
            results.append("Direct reply in group chat: PASS")
        else:
            results.append("Direct reply in group chat: FAIL")
        sc.async_run_signal_cli = original_async_run
    except Exception as e:
        results.append(f"Direct reply in group chat: FAIL ({e})")
    
    # Test 6: Indirect reply in private message (simulate send_message)
    try:
        original_async_run = sc.async_run_signal_cli
        calls = []
        async def dummy_async_run(args):
            calls.append(args)
            return "dummy output"
        sc.async_run_signal_cli = dummy_async_run
        
        # Call send_message as if in a private chat (no group_id).
        await sc.send_message(
            to_number="+111",
            message="Private message"
        )
        # Verify that the arguments do not include group flags or reply quoting flags.
        args_str = " ".join(calls[0])
        if "-g" not in args_str and "--quote-author" not in args_str:
            results.append("Indirect reply in private chat: PASS")
        else:
            results.append("Indirect reply in private chat: FAIL")
        sc.async_run_signal_cli = original_async_run
    except Exception as e:
        results.append(f"Indirect reply in private chat: FAIL ({e})")
    
    # Test 7: Invalid command handling
    try:
        # Create a ParsedMessage with an unrecognized command.
        parsed_invalid = ParsedMessage(
            sender="+123",
            body="nonexistent",
            timestamp=0,
            group_id=None,
            reply_to=None,
            message_timestamp=None,
            command="nonexistent",
            args=""
        )
        # handle_message should return an empty string for unrecognized commands.
        result = handle_message(parsed_invalid, "+123", BotStateMachine())
        if result == "":
            results.append("Invalid command handling: PASS")
        else:
            results.append("Invalid command handling: FAIL")
    except Exception as e:
        results.append(f"Invalid command handling: FAIL ({e})")
    
    summary = "\n".join(results)
    return summary

def run_all_tests() -> None:
    """
    Run all integration tests and print the summary.
    """
    summary = asyncio.run(run_tests())
    print("Integration Test Summary:\n" + summary)

if __name__ == "__main__":
    run_all_tests()

# End of tests/test_all.py