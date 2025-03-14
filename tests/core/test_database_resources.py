#!/usr/bin/env python
"""
tests/core/test_database_resources.py – Tests for the resource database operations.
Verifies that add_resource, list_resources, and remove_resource function as expected.
"""

from db.resources import add_resource, list_resources, remove_resource

def test_add_and_list_resource():
    # Add a resource and verify that it appears in the list for the given category.
    resource_id = add_resource("Linktree", "https://linktr.ee/50501oc", "Official Linktree")
    assert resource_id > 0
    
    resources = list_resources("Linktree")
    assert any(res["id"] == resource_id and res["url"] == "https://linktr.ee/50501oc" for res in resources)

def test_remove_resource():
    # Add a resource and then remove it.
    resource_id = add_resource("Linktree", "https://linktr.ee/50501oc", "Official Linktree")
    resources = list_resources("Linktree")
    assert any(res["id"] == resource_id for res in resources)
    
    remove_resource(resource_id)
    
    resources_after = list_resources("Linktree")
    assert not any(res["id"] == resource_id for res in resources_after)

# End of tests/core/test_database_resources.py