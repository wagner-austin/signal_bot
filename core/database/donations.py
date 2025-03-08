#!/usr/bin/env python
"""
core/database/donations.py - Donation database operations using repository pattern.
Provides functions for adding donation records to the Donations table.
"""

from core.database.repository import DonationRepository

def add_donation(phone: str, amount: float, donation_type: str, description: str) -> int:
    repo = DonationRepository()
    data = {
        "phone": phone,
        "amount": amount,
        "donation_type": donation_type,
        "description": description
    }
    return repo.create(data)

# End of core/database/donations.py