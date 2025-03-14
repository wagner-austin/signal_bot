#!/usr/bin/env python
"""
core/signal_client.py --- Encapsulates functions to interact with signal-cli.
Uses MessageManager for processing incoming messages and sending responses.
Supports dependency injection for the logger.
"""

import asyncio
import re
import logging
from typing import List, Optional, Tuple
from core.signal_cli_runner import async_run_signal_cli, SignalCLIError
from parsers.message_parser import parse_message, ParsedMessage
from managers.message_manager import MessageManager

logger = logging.getLogger(__name__)

async def send_message(
    to_number: str,
    message: str,
    group_id: Optional[str] = None,
    reply_quote_author: Optional[str] = None,
    reply_quote_timestamp: Optional[str] = None,
    reply_quote_message: Optional[str] = None,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    send_message - Asynchronously send a message using signal-cli.
    Accepts an optional logger dependency.
    """
    if logger is None:
        logger = logging.getLogger(__name__)
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

async def receive_messages(logger: Optional[logging.Logger] = None) -> List[str]:
    """
    receive_messages - Asynchronously retrieve incoming messages using signal-cli.
    Accepts an optional logger dependency.
    """
    if logger is None:
        logger = logging.getLogger(__name__)
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
    _get_quote_details - Extract quoting details from a parsed message.
    Returns a tuple of (quote_timestamp, quote_author, quote_message).
    """
    msg_timestamp = parsed.timestamp
    quote_timestamp = str(parsed.message_timestamp or msg_timestamp) if msg_timestamp else None
    quote_author = parsed.sender
    quote_message = parsed.body
    return quote_timestamp, quote_author, quote_message

async def _dispatch_message(response: str, parsed: ParsedMessage, quote_details: Tuple[Optional[str], str, str], logger: Optional[logging.Logger] = None) -> None:
    """
    _dispatch_message - Dispatch the response message using send_message with quoting details.
    Accepts an optional logger dependency.
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    await send_message(
        parsed.sender,
        response,
        group_id=parsed.group_id,
        reply_quote_author=quote_details[1],
        reply_quote_timestamp=quote_details[0],
        reply_quote_message=quote_details[2],
        logger=logger
    )

async def process_incoming(state_machine, logger: Optional[logging.Logger] = None) -> int:
    """
    process_incoming - Process incoming messages, dispatch commands, and send responses.
    Accepts an optional logger dependency.
    Returns the number of processed messages.
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    from managers.volunteer_manager import VOLUNTEER_MANAGER
    from core.database import get_volunteer_record
    from managers.user_states_manager import has_seen_welcome, mark_welcome_seen
    from core.messages import GETTING_STARTED

    messages = await receive_messages(logger=logger)
    processed_count = 0
    message_manager = MessageManager(state_machine)
    for message in messages:
        logger.info(f"Processing message:\n{message}\n")
        parsed = parse_message(message)
        if not parsed.sender or not parsed.body:
            logger.warning(f"Skipping message due to missing sender or body. Parsed: {parsed}")
            continue
        processed_count += 1
        # If sender is unregistered and has not seen the welcome message, send GETTING_STARTED separately.
        if get_volunteer_record(parsed.sender) is None and not has_seen_welcome(parsed.sender):
            await send_message(parsed.sender, GETTING_STARTED)
            mark_welcome_seen(parsed.sender)
        quote_details = _get_quote_details(parsed)
        response = message_manager.process_message(parsed, parsed.sender, VOLUNTEER_MANAGER, msg_timestamp=parsed.timestamp)
        if asyncio.iscoroutine(response):
            response = await response
        if response:
            await _dispatch_message(response, parsed, quote_details, logger=logger)
    return processed_count

# End of core/signal_client.py