#!/usr/bin/env python
"""
cli/common.py - Common CLI helper functions.
Provides helper functions to standardize output formatting for CLI commands.
"""

def print_results(data, formatter, empty_message="No data found."):
    """
    Print formatted results from a list of records.
    
    Args:
        data (iterable): An iterable of records.
        formatter (callable): Function that takes a record and returns a formatted string.
        empty_message (str): Message to print if no records are found.
    """
    if not data:
        print(empty_message)
        return
    for record in data:
        print(formatter(record))

# End of cli/common.py