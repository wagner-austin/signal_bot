#!/usr/bin/env python
"""
plugins/commands/subcommand_dispatcher.py - Utility for dispatching subcommands.
Provides a high-level `handle_subcommands(...)` function that consolidates
subcommand parsing, including automatic empty-argument validation.
"""

from typing import List, Dict, Callable, Optional
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import PluginArgError


def dispatch_subcommand(tokens: List[str],
                        subcommands: Dict[str, Callable[..., str]],
                        usage_msg: str = None,
                        unknown_subcmd_msg: str = None) -> str:
    """
    dispatch_subcommand - Utility for plugin subcommand dispatch.

    Args:
        tokens (List[str]): The list of tokens (positional arguments).
        subcommands (Dict[str, Callable[..., str]]): Mapping of subcommand name -> handler function.
        usage_msg (str, optional): Shown if no subcommand was provided or appended if subcommand is unrecognized.
        unknown_subcmd_msg (str, optional): Shown if the subcommand is unrecognized.

    Returns:
        str: The result of the subcommand handler.

    Raises:
        PluginArgError: If no subcommand was specified or if the subcommand is unrecognized.
    """
    if not tokens:
        final_msg = usage_msg or "No subcommand specified."
        raise PluginArgError(final_msg)

    cmd = tokens[0].lower()
    rest = tokens[1:]

    if cmd not in subcommands:
        msg_parts = []
        if unknown_subcmd_msg:
            msg_parts.append(unknown_subcmd_msg)
        if usage_msg:
            msg_parts.append(usage_msg)
        if not msg_parts:
            msg_parts = [f"Unknown subcommand '{cmd}'."]
        combined_message = "\n\n".join(msg_parts)
        raise PluginArgError(combined_message)

    return subcommands[cmd](rest)


def handle_subcommands(args: str,
                       subcommands: Dict[str, Callable[[List[str]], str]],
                       usage_msg: str,
                       unknown_subcmd_msg: str = "Unknown subcommand",
                       parse_mode: str = 'positional',
                       parse_maxsplit: int = -1,
                       default_subcommand: Optional[str] = None) -> str:
    """
    handle_subcommands - High-level wrapper for subcommand-based plugin commands.
      1) Parses 'args' into tokens using parse_plugin_arguments.
      2) If args is empty and a default_subcommand is provided, forces tokens to [default_subcommand].
      3) Otherwise, if args is empty, immediately raises a PluginArgError with the usage message.
      4) Dispatches the tokens to the appropriate subcommand handler.

    Args:
        args (str): The raw argument string for the plugin command.
        subcommands (Dict[str, Callable[[List[str]], str]]): Map of subcommand name -> function.
        usage_msg (str): The usage message to show on errors or when no arguments are provided.
        unknown_subcmd_msg (str, optional): Shown if subcommand is unrecognized. Defaults to "Unknown subcommand".
        parse_mode (str): Mode to pass to parse_plugin_arguments (usually 'positional' or 'kv').
        parse_maxsplit (int): Maximum splits for parse_plugin_arguments. Defaults to -1 (no limit).
        default_subcommand (Optional[str]): Name of the subcommand to use if no tokens are parsed.

    Returns:
        str: The response from the chosen subcommand or usage text on error.
    """
    if not args.strip():
        if default_subcommand:
            tokens = [default_subcommand]
        else:
            raise PluginArgError(usage_msg)
    else:
        parsed = parse_plugin_arguments(args, mode=parse_mode, maxsplit=parse_maxsplit)
        tokens = parsed["tokens"]
        if not tokens and default_subcommand:
            tokens = [default_subcommand]
        elif not tokens:
            raise PluginArgError(usage_msg)

    return dispatch_subcommand(tokens, subcommands, usage_msg, unknown_subcmd_msg)

# End of plugins/commands/subcommand_dispatcher.py