#!/usr/bin/env python
"""
File: tests/managers/test_resources_manager.py
----------------------------------------------
Tests for resource manager functionalities.
Verifies that the unified function list_all_resources returns all resource records correctly,
and that invalid URLs raise a ResourceError.
"""

import pytest
from managers.resources_manager import list_all_resources, create_resource, delete_resource
from db.resources import add_resource, remove_resource
from core.exceptions import ResourceError

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

def test_create_resource_with_invalid_url():
    """
    Confirm that create_resource raises ResourceError if url doesn't start with 'http'.
    """
    with pytest.raises(ResourceError, match="URL must start with 'http'"):
        create_resource("BadCat", "ftp://example.com/resource", "Bad Resource")

def test_create_resource_and_delete():
    """
    Confirm a resource can be created via create_resource and then deleted via delete_resource.
    """
    resource_id = create_resource("Blog", "http://exampleblog.com", "Sample Blog")
    assert resource_id > 0
    all_resources = list_all_resources()
    assert any(r["id"] == resource_id for r in all_resources), "New resource should appear in the list."
    delete_resource(resource_id)
    all_resources_after = list_all_resources()
    assert not any(r["id"] == resource_id for r in all_resources_after), "Resource should be removed after delete."

# End of tests/managers/test_resources_manager.py