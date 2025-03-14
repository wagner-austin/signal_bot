#!/usr/bin/env python
"""
db/donations.py
------------
Donation database operations using a repository pattern.
(Moved from core/database/donations.py)
"""

from db.repository import DonationRepository

def add_donation(phone: str, amount: float, donation_type: str, description: str) -> int:
    """
    add_donation - Insert a donation record into the Donations table via the DonationRepository.

    Args:
        phone (str): The donor's phone number.
        amount (float): Monetary amount (0.0 if in-kind).
        donation_type (str): "cash", "in-kind", or "register".
        description (str): Additional info about the donation.

    Returns:
        int: The database row ID of the newly created donation record.
    """
    repo = DonationRepository()
    data = {
        "phone": phone,
        "amount": amount,
        "donation_type": donation_type,
        "description": description
    }
    return repo.create(data)

# End of db/donations.py