#!/usr/bin/env python
"""
core/signal_client.py - Encapsulates functions to interact with signal-cli.
Uses MessageManager for processing incoming messages and sending responses.
"""

import asyncio
import re
import logging
from typing import List, Optional, Tuple
from core.signal_cli_runner import async_run_signal_cli, SignalCLIError
from parsers.message_parser import parse_message, ParsedMessage

# Updated: Import the aggregated facade instead of the removed message_handler.
from managers.message_manager import MessageManager

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
    
    Parameters:
        to_number (str): Recipient number.
        message (str): Message text.
        group_id (Optional[str]): Group ID if applicable.
        reply_quote_author (Optional[str]): Author of the quoted message.
        reply_quote_timestamp (Optional[str]): Timestamp of the quoted message.
        reply_quote_message (Optional[str]): The quoted message text.
        
    Returns:
        None
    """
    if group_id:
        args = ['send', '-g', group_id]
    else:
        args = ['send', to_number]
    
    if group_id and reply_quote_author and reply_quote_timestamp and reply_quote_message:
        args.extend([
            '--quote-author', reply_quote_author,
            '--quote-timestamp', reply_quote_timestamp,
            '--quote-message', reply_quote_message
        ])
    
    args.append('--message-from-stdin')
    
    if group_id:
        logger.info(f"Sent to group {group_id}: {message} (replying to message by {reply_quote_author})")
    else:
        logger.info(f"Sent to {to_number}: {message} (individual chat)")
    await async_run_signal_cli(args, stdin_input=message)
    
    from core.metrics import increment_message_count
    increment_message_count()

async def receive_messages() -> List[str]:
    """
    Asynchronously retrieve incoming messages using signal-cli.
    
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

    Returns:
        Tuple[Optional[str], str, str]: quote_timestamp, quote_author, quote_message.
    """
    msg_timestamp = parsed.timestamp
    quote_timestamp = str(parsed.message_timestamp or msg_timestamp) if msg_timestamp else None
    quote_author = parsed.sender
    quote_message = parsed.body
    return quote_timestamp, quote_author, quote_message

async def _dispatch_message(response: str, parsed: ParsedMessage, quote_details: Tuple[Optional[str], str, str]) -> None:
    """
    Dispatch the response message using send_message with quoting details.
    
    Parameters:
        response (str): Response text.
        parsed (ParsedMessage): Parsed original message.
        quote_details (Tuple[Optional[str], str, str]): Quoting details.
        
    Returns:
        None
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
        int: Number of processed messages.
    """
    from managers.pending_actions import PENDING_ACTIONS
    from managers.volunteer_manager import VOLUNTEER_MANAGER

    messages = await receive_messages()
    processed_count = 0
    # Instantiate the aggregated MessageManager
    message_manager = MessageManager(state_machine)
    for message in messages:
        logger.info(f"Processing message:\n{message}\n")
        parsed = parse_message(message)
        if not parsed.sender or not parsed.body:
            continue
        processed_count += 1
        quote_details = _get_quote_details(parsed)
        response = message_manager.process_message(parsed, parsed.sender, PENDING_ACTIONS, VOLUNTEER_MANAGER, msg_timestamp=parsed.timestamp)
        if asyncio.iscoroutine(response):
            response = await response
        if response:
            await _dispatch_message(response, parsed, quote_details)
    return processed_count

# End of core/signal_client.py