"""Grant derive primitive functions — capability-name-to-typed-model binding.

CC=1. No branching. No cross-module dependencies.

Type-wrapping layer for the grant derivation pipeline. Bridges the gap between
the capability-name string domain (read, search, inspect, write, edit, append)
and the typed Enforcement model domain (EnforcementExplicitRead, etc.).

Each of the six capabilities has its own typed wrapper because downstream
consumers need to distinguish capability semantics — a Read grant enables
file content access, while a Search grant enables content matching. The
models are schema-generated Pydantic types that carry the granted path list.
"""

from regin.structure.gen.schema.agent_permissions_resolved import (
    EnforcementExplicitAppend,
    EnforcementExplicitEdit,
    EnforcementExplicitInspect,
    EnforcementExplicitRead,
    EnforcementExplicitSearch,
    EnforcementExplicitWrite,
)


def wrap_capability_paths(capability: str, paths: list[str]):
    """Wrap a path list in the typed model for the given capability name.

    The mapping table is the single source of truth for capability-name-to-model
    binding. Each capability name corresponds to exactly one Enforcement model type.
    Called once per capability during grant derivation, after path intersection
    and containment collapse have produced the final path list for that capability.
    """
    # Capability-name -> typed enforcement model. One entry per abstract capability.
    models = {
        "read": EnforcementExplicitRead,
        "search": EnforcementExplicitSearch,
        "inspect": EnforcementExplicitInspect,
        "write": EnforcementExplicitWrite,
        "edit": EnforcementExplicitEdit,
        "append": EnforcementExplicitAppend,
    }
    return models[capability](paths)
