#!/usr/bin/env python
"""
parsers/argument_parser.py - Argument parsing utilities.
Provides common functions for splitting command arguments and parsing key-value pairs,
centralizing repetitive string splitting and validation logic.
"""

def split_args(args: str, sep: str = None, maxsplit: int = -1) -> list:
    """
    Splits the argument string into tokens.
    
    Args:
        args (str): The raw argument string.
        sep (str, optional): The delimiter to use for splitting. Defaults to None (whitespace splitting).
        maxsplit (int, optional): Maximum number of splits. Defaults to -1 (no limit).
    
    Returns:
        list: List of tokens.
    """
    if sep is None:
        return args.strip().split(maxsplit=maxsplit)
    else:
        return [token.strip() for token in args.split(sep, maxsplit) if token.strip()]

def parse_key_value_args(args: str, pair_delimiter: str = ",", key_value_separator: str = ":") -> dict:
    """
    Parses a string into a dictionary by splitting using the pair delimiter and key-value separator.
    
    Args:
        args (str): The raw argument string.
        pair_delimiter (str, optional): Delimiter between key-value pairs. Defaults to ",".
        key_value_separator (str, optional): Separator between key and value. Defaults to ":".
    
    Returns:
        dict: Dictionary of parsed key-value pairs.
    
    Raises:
        ValueError: If a pair does not contain the key-value separator.
    """
    result = {}
    pairs = [pair.strip() for pair in args.split(pair_delimiter) if pair.strip()]
    for pair in pairs:
        if key_value_separator not in pair:
            raise ValueError(f"Argument '{pair}' is not a valid key{key_value_separator}value pair.")
        key, value = pair.split(key_value_separator, 1)
        result[key.strip().lower()] = value.strip()
    return result

# End of parsers/argument_parser.py