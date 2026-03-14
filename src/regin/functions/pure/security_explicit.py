"""Derive explicit grants from author-defined path and capability declarations.

Intersects declared paths with requested capabilities minus prohibited.
System 1 — displayed to agent in Security Boundary section.

Pure — reads typed models, returns typed model.
"""

from regin.functions.pure.path_operations import (
    collapse_path_containment,
    intersect_paths_capabilities,
)
from regin.structures.schema.agent_paths_resolved import Capabilities, Security
from regin.structures.schema.agent_permissions_resolved import (
    EnforcementExplicitAppend,
    EnforcementExplicitEdit,
    EnforcementExplicitGrants,
    EnforcementExplicitInspect,
    EnforcementExplicitRead,
    EnforcementExplicitSearch,
    EnforcementExplicitWrite,
)


def wrap_capability_paths(capability: str, paths: list[str]):
    """Wrap a path list in the typed model for the given capability name."""
    models = {
        "read": EnforcementExplicitRead,
        "search": EnforcementExplicitSearch,
        "inspect": EnforcementExplicitInspect,
        "write": EnforcementExplicitWrite,
        "edit": EnforcementExplicitEdit,
        "append": EnforcementExplicitAppend,
    }
    return models[capability](paths)


def derive_explicit_grants(security: Security) -> EnforcementExplicitGrants:
    """Intersect paths with capabilities, collapse, return typed grants."""
    paths = security.security_paths
    read_paths = [entry.root for entry in paths.paths_allowed_read.root] if paths.paths_allowed_read else []
    write_paths = [entry.root for entry in paths.paths_allowed_write.root] if paths.paths_allowed_write else []
    caps = security.security_capabilities
    requested = {Capabilities(cap.value) for cap in caps.capabilities_requested.root} if caps else set()
    prohibited = {Capabilities(cap.value) for cap in caps.capabilities_prohibited.root} if caps and caps.capabilities_prohibited else set()
    raw_grants = intersect_paths_capabilities(read_paths, write_paths, requested, prohibited)
    collapsed = collapse_path_containment(raw_grants)
    fields = {cap: wrap_capability_paths(cap, cap_paths) for cap, cap_paths in collapsed.items()}
    return EnforcementExplicitGrants(**fields)
