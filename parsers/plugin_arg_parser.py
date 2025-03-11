#!/usr/bin/env python
"""
parsers/plugin_arg_parser.py - Pydantic-based plugin argument parser.
Provides typed Pydantic models and a unified validate_model function for argument validation.
Raises PluginArgError on invalid arguments.
"""

from typing import Optional, List, Type, TypeVar
from pydantic import BaseModel, ValidationError, PositiveInt, HttpUrl

# -----------------------------
# Exception for usage errors
# -----------------------------
class PluginArgError(Exception):
    """Custom exception raised when plugin argument parsing fails."""
    pass

# -----------------------------
# Resource Command Models
# -----------------------------
class ResourceAddModel(BaseModel):
    category: str
    url: HttpUrl
    title: Optional[str] = ""

class ResourceListModel(BaseModel):
    category: Optional[str] = None

class ResourceRemoveModel(BaseModel):
    id: PositiveInt

# -----------------------------
# Event Command Models
# -----------------------------
class PlanEventModel(BaseModel):
    """Used by 'plan event' subcommand."""
    title: str
    date: str
    time: str
    location: str
    description: str

class EditEventModel(BaseModel):
    """Used by 'edit event' subcommand."""
    event_id: PositiveInt
    title: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None

class RemoveEventByIdModel(BaseModel):
    """Used by 'remove event' with an EventID."""
    event_id: PositiveInt

class RemoveEventByTitleModel(BaseModel):
    """Used by 'remove event' with a Title."""
    title: str

# -----------------------------
# Task Command Models
# -----------------------------
class TaskAddModel(BaseModel):
    description: str

class TaskAssignModel(BaseModel):
    task_id: PositiveInt
    volunteer_display_name: str

class TaskCloseModel(BaseModel):
    task_id: PositiveInt

# -----------------------------
# Role Command Models
# -----------------------------
class RoleSetModel(BaseModel):
    role: str

class RoleSwitchModel(BaseModel):
    role: str

# -----------------------------
# System Command Models
# (for '@bot assign <skill>')
# -----------------------------
class SystemAssignModel(BaseModel):
    skill: str

# -----------------------------
# Donate Command Models
# -----------------------------
class CashDonationArgs(BaseModel):
    amount: float
    description: str

class InKindDonationArgs(BaseModel):
    description: str

class RegisterDonationArgs(BaseModel):
    method: str
    description: Optional[str] = ""

# -----------------------------
# Volunteer Command Models
# -----------------------------
class VolunteerFindModel(BaseModel):
    skills: List[str]

class VolunteerAddSkillsModel(BaseModel):
    skills: List[str]

# -----------------------------
# Unified model validation helper
# -----------------------------
T = TypeVar("T", bound=BaseModel)

def validate_model(data: dict, model: Type[T], usage: str) -> T:
    """
    validate_model - Validate a data dictionary against a Pydantic model.
    Raises PluginArgError with a uniform "Usage error:" message on validation failure.
    
    Args:
        data (dict): Data dictionary to validate.
        model (Type[BaseModel]): Pydantic model class.
        usage (str): Usage message to display in error.
    
    Returns:
        An instance of the model.
    
    Raises:
        PluginArgError: If validation fails.
    """
    try:
        return model.model_validate(data)
    except ValidationError as ve:
        raise PluginArgError(f"Usage error: {usage}\n{ve}")

# End of parsers/plugin_arg_parser.py