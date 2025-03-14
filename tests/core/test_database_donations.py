#!/usr/bin/env python
"""
tests/core/test_database_donations.py - Tests for donation database operations.
Verifies that add_donation correctly inserts a donation record into the Donations table.
"""

from db.donations import add_donation
from db.connection import get_connection

def test_add_donation():
    phone = "+9999999999"
    amount = 50.0
    donation_type = "cash"
    description = "Test cash donation"
    donation_id = add_donation(phone, amount, donation_type, description)
    assert donation_id > 0

    # Verify that the donation record exists in the Donations table
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT phone, amount, donation_type, description FROM Donations WHERE id = ?", (donation_id,))
    row = cursor.fetchone()
    conn.close()
    assert row is not None
    assert row["phone"] == phone
    assert row["amount"] == amount
    assert row["donation_type"] == donation_type
    assert row["description"] == description

def test_add_in_kind_donation():
    phone = "+8888888888"
    amount = 0.0
    donation_type = "in-kind"
    description = "Test in-kind donation: 20 chairs"
    donation_id = add_donation(phone, amount, donation_type, description)
    assert donation_id > 0

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT donation_type, description FROM Donations WHERE id = ?", (donation_id,))
    row = cursor.fetchone()
    conn.close()
    assert row is not None
    assert row["donation_type"] == donation_type
    assert "20 chairs" in row["description"]

def test_add_donation_register():
    phone = "+7777777777"
    amount = 0.0
    donation_type = "venmo"
    description = "Register interest for venmo donation"
    donation_id = add_donation(phone, amount, donation_type, description)
    assert donation_id > 0

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT donation_type FROM Donations WHERE id = ?", (donation_id,))
    row = cursor.fetchone()
    conn.close()
    assert row is not None
    assert row["donation_type"] == donation_type

# End of tests/core/test_database_donations.py