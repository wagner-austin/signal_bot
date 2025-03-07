"""
core/signal_client.py - Encapsulates functions to interact with signal-cli for sending and receiving messages.
Now uses the --message-from-stdin flag to send multi-line messages via STDIN.
Includes graceful handling of timeouts during message receiving.
"""

import asyncio
import re
import logging
from typing import List, Optional, Tuple
from core.signal_cli_runner import async_run_signal_cli, SignalCLIError
from managers.message_handler import handle_message
from parsers.message_parser import parse_message, ParsedMessage

logger = logging.getLogger(__name__)

async def send_message(
    to_number: str,
    message: str,
    group_id: Optional[str] = None,
    reply_quote_author: Optional[str] = None,
    reply_quote_timestamp: Optional[str] = None,
    reply_quote_message: Optional[str] = None
) -> None:
    """
    Asynchronously send a message using signal-cli.
    
    For group chats, includes direct reply quoting if available.
    For individual chats, sends without quoting.
    Uses the new --message-from-stdin flag to pass message content via STDIN.
    """
    if group_id:
        args = ['send', '-g', group_id]
    else:
        args = ['send', to_number]
    
    # For group chats, include quoting flags if available.
    if group_id and reply_quote_author and reply_quote_timestamp and reply_quote_message:
        args.extend([
            '--quote-author', reply_quote_author,
            '--quote-timestamp', reply_quote_timestamp,
            '--quote-message', reply_quote_message
        ])
    
    # Use the new flag to pass message content via STDIN.
    args.append('--message-from-stdin')
    
    if group_id:
        logger.info(f"Sent to group {group_id}: {message} (replying to message by {reply_quote_author})")
    else:
        logger.info(f"Sent to {to_number}: {message} (individual chat)")
    await async_run_signal_cli(args, stdin_input=message)
    
    # Increment message count after successful send.
    from core.metrics import increment_message_count
    increment_message_count()

async def receive_messages() -> List[str]:
    """
    Asynchronously retrieve incoming messages using signal-cli.
    Gracefully handles timeouts by logging the error and returning an empty list.
    
    Returns:
        List[str]: A list of raw message strings.
    """
    try:
        output = await async_run_signal_cli(['receive'], stdin_input=None)
    except SignalCLIError as e:
        logger.error(f"Error receiving messages: {e}")
        return []
    if output:
        messages = re.split(r'\n(?=Envelope)', output.strip())
        return messages
    return []

def _get_quote_details(parsed: ParsedMessage) -> Tuple[Optional[str], str, str]:
    """
    Extract quoting details from a parsed message.
    """
    msg_timestamp = parsed.timestamp
    quote_timestamp = str(parsed.message_timestamp or msg_timestamp) if msg_timestamp else None
    quote_author = parsed.sender
    quote_message = parsed.body
    return quote_timestamp, quote_author, quote_message

async def _dispatch_message(response: str, parsed: ParsedMessage, quote_details: Tuple[Optional[str], str, str]) -> None:
    """
    Dispatch the response message using send_message with quoting details.
    """
    await send_message(
        parsed.sender,
        response,
        group_id=parsed.group_id,
        reply_quote_author=quote_details[1],
        reply_quote_timestamp=quote_details[0],
        reply_quote_message=quote_details[2]
    )

async def process_incoming(state_machine) -> int:
    """
    Process incoming messages, dispatch commands, and send responses.
    
    Returns:
        int: The count of processed messages.
    """
    # Import global dependencies explicitly and pass them to the handler.
    from managers.pending_actions import PENDING_ACTIONS
    from managers.volunteer_manager import VOLUNTEER_MANAGER

    messages = await receive_messages()
    processed_count = 0
    for message in messages:
        logger.info(f"Processing message:\n{message}\n")
        
        parsed = parse_message(message)
        if not parsed.sender or not parsed.body:
            continue
        
        processed_count += 1
        quote_details = _get_quote_details(parsed)
        response = handle_message(
            parsed,
            parsed.sender,
            state_machine,
            PENDING_ACTIONS,
            VOLUNTEER_MANAGER,
            msg_timestamp=parsed.timestamp
        )
        if asyncio.iscoroutine(response):
            response = await response
        if response:
            await _dispatch_message(response, parsed, quote_details)
    return processed_count

# End of core/signal_client.py
