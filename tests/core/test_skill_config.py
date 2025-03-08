#!/usr/bin/env python
"""
tests/core/test_skill_config.py - Tests for core/skill_config.
Verifies that AVAILABLE_SKILLS is a non-empty list of strings.
"""
from core.skill_config import AVAILABLE_SKILLS

def test_available_skills_list():
    assert isinstance(AVAILABLE_SKILLS, list)
    assert len(AVAILABLE_SKILLS) > 0
    for skill in AVAILABLE_SKILLS:
        assert isinstance(skill, str) and skill.strip() != ""

# End of tests/core/test_skill_config.py