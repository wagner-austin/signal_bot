#!/usr/bin/env python
"""
tests/managers/test_resources_manager.py - Tests for resource manager functionalities.
Verifies that the unified function list_all_resources returns all resource records correctly.
"""

from managers.resources_manager import list_all_resources
from core.database.resources import add_resource, remove_resource
import pytest

def test_list_all_resources_empty():
    # When no resources exist, list_all_resources should return an empty list.
    resources = list_all_resources()
    assert isinstance(resources, list)
    # It is acceptable for the list to be empty.

def test_list_all_resources_after_add():
    # Add a resource.
    resource_id = add_resource("TestCat", "https://example.com/resource", "Test Resource")
    resources = list_all_resources()
    # Verify that the added resource is present in the list.
    found = any(res["id"] == resource_id and res["title"] == "Test Resource" for res in resources)
    assert found, "Added resource not found in list_all_resources"
    # Clean up by removing the added resource.
    remove_resource(resource_id)

# End of tests/managers/test_resources_manager.py