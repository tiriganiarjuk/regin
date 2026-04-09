"""Dispatch table mapping capability names to enforcement model constructors.

Maps the six abstract capability names (read, search, inspect, write, edit,
append) to their corresponding typed EnforcementExplicit* Pydantic models.
Used by assembled.py during grant derivation to wrap collapsed path lists
in the correct model type for each capability.
"""

from collections.abc import Callable

from pydantic import BaseModel

from regin.structure.gen.schema.agent_permissions_resolved import (
    EnforcementExplicitAppend,
    EnforcementExplicitEdit,
    EnforcementExplicitInspect,
    EnforcementExplicitRead,
    EnforcementExplicitSearch,
    EnforcementExplicitWrite,
)

CAPABILITY_MODELS: dict[str, Callable[[list[str]], BaseModel]] = {
    "read": EnforcementExplicitRead,
    "search": EnforcementExplicitSearch,
    "inspect": EnforcementExplicitInspect,
    "write": EnforcementExplicitWrite,
    "edit": EnforcementExplicitEdit,
    "append": EnforcementExplicitAppend,
}
