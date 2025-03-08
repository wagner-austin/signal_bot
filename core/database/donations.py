#!/usr/bin/env python
"""
core/database/donations.py - Donation database operations.
Provides functions for adding donation records to the Donations table.
"""

from .helpers import execute_sql
from .connection import db_connection

def add_donation(phone: str, amount: float, donation_type: str, description: str) -> int:
    """
    Add a new donation record to the Donations table.
    
    Args:
        phone (str): The donor's phone number.
        amount (float): The donation amount (use 0.0 for non-cash donations).
        donation_type (str): Type of donation (e.g. "cash", "venmo", "in-kind", or a registered method).
        description (str): Additional description of the donation.
        
    Returns:
        int: The ID of the newly added donation record.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Donations (phone, amount, donation_type, description) VALUES (?, ?, ?, ?)",
            (phone, amount, donation_type, description)
        )
        conn.commit()
        donation_id = cursor.lastrowid
    return donation_id

# End of core/database/donations.py