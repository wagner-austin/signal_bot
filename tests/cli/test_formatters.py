#!/usr/bin/env python
"""
tests/cli/test_formatters.py - Tests for CLI formatters.
Verifies that each formatting function in cli/formatters.py returns the expected output when provided with sample data.
"""

from cli.formatters import (
    format_event,
    format_event_speaker,
    format_log,
    format_resource,
    format_task,
    format_volunteer,
    format_deleted_volunteer
)

def test_format_event():
    sample = {
        'event_id': 1,
        'title': 'Test Event',
        'date': '2025-03-09',
        'time': '2-4PM',
        'location': 'Test Location',
        'description': 'Test Description'
    }
    output = format_event(sample)
    assert "Event ID: 1" in output
    assert "Title: Test Event" in output
    assert "Date: 2025-03-09" in output
    assert "Time: 2-4PM" in output
    assert "Location: Test Location" in output
    assert "Description: Test Description" in output
    assert "-" * 40 in output

def test_format_event_speaker():
    sample = {
        'id': 2,
        'event_id': 1,
        'speaker_name': 'Speaker One',
        'speaker_topic': 'Topic A',
        'created_at': '2025-03-09 12:00:00'
    }
    output = format_event_speaker(sample)
    assert "ID: 2" in output
    assert "Event ID: 1" in output
    assert "Speaker Name: Speaker One" in output
    assert "Speaker Topic: Topic A" in output
    assert "Created At: 2025-03-09 12:00:00" in output

def test_format_log():
    sample = {
        'id': 3,
        'sender': '+3333333333',
        'command': 'test',
        'args': 'arg1 arg2',
        'timestamp': '2025-03-09 12:00:00'
    }
    output = format_log(sample)
    assert "ID: 3" in output
    assert "Sender: +3333333333" in output
    assert "Command: test" in output
    assert "Args: arg1 arg2" in output
    assert "Timestamp: 2025-03-09 12:00:00" in output

def test_format_resource():
    sample = {
        'id': 4,
        'category': 'Linktree',
        'title': 'Official Linktree',
        'url': 'https://linktr.ee/50501oc',
        'created_at': '2025-03-09 12:00:00'
    }
    output = format_resource(sample)
    assert "ID: 4" in output
    assert "Category: Linktree" in output
    assert "Title: Official Linktree" in output
    assert "URL: https://linktr.ee/50501oc" in output
    assert "Created At: 2025-03-09 12:00:00" in output

def test_format_task():
    sample = {
        'task_id': 5,
        'description': 'Test Task',
        'status': 'open',
        'created_at': '2025-03-09 12:00:00',
        'created_by_name': 'John Doe',
        'assigned_to_name': 'Jane Smith'
    }
    output = format_task(sample)
    assert "Task ID: 5" in output
    assert "Description: Test Task" in output
    assert "Status: open" in output
    assert "Created By: John Doe" in output
    assert "Assigned To: Jane Smith" in output

def test_format_volunteer():
    sample = {
        'phone': "+1111111111",
        'name': 'John Doe',
        'skills': ['Python', 'SQL'],
        'available': True,
        'current_role': 'Coordinator'
    }
    output = format_volunteer(sample)
    assert "Phone: +1111111111" in output
    assert "Name: John Doe" in output
    assert "Skills: Python, SQL" in output
    assert "Available: True" in output
    assert "Current Role: Coordinator" in output

def test_format_deleted_volunteer():
    sample = {
        'phone': "+2222222222",
        'name': "Deleted Volunteer",
        'skills': "SkillA,SkillB",
        'available': 0,
        'current_role': "",
        'deleted_at': "2025-03-09 12:00:00"
    }
    output = format_deleted_volunteer(sample)
    assert "Phone: +2222222222" in output
    assert "Name: Deleted Volunteer" in output
    # Updated expectation to include a space after the comma
    assert "Skills: SkillA, SkillB" in output
    assert "Available: 0" in output
    assert "Current Role: " in output
    assert "Deleted At: 2025-03-09 12:00:00" in output

# End of tests/cli/test_formatters.py