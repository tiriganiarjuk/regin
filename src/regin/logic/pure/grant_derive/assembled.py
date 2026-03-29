"""Grant derive assembled — explicit grant derivation entry point.

CC=1-2. Imports from composed, simple, and primitive within this module.
Path operations injected via DI to avoid Composed->Composed import.

Explicit grants are the intersection of author-declared paths with author-
requested capabilities. This is the "positive permission" path — the author
says "I want these capabilities on these paths."

DI injection of intersect_fn and collapse_fn allows the assembled layer to
compose pure functions without cross-module Composed imports (which would
violate the same-level import ban that prevents monolith formation).
"""

from regin.logic.pure.grant_derive.composed import extract_prohibited
from regin.logic.pure.grant_derive.primitive import wrap_capability_paths
from regin.logic.pure.grant_derive.simple import (
    extract_read_paths,
    extract_requested,
    extract_write_paths,
)
from regin.logic.pure.path_operations.simple import PathCollapser, PathIntersector
from regin.structure.gen.schema.agent_paths_resolved import Security
from regin.structure.gen.schema.agent_permissions_resolved import (
    EnforcementExplicitGrants,
)


def derive_explicit_grants(
    security: Security,
    intersect_fn: PathIntersector,
    collapse_fn: PathCollapser,
) -> EnforcementExplicitGrants:
    """Run the full explicit grant derivation pipeline.

    Pipeline steps:
    1. Extract raw paths (read, write) and capability sets (requested, prohibited)
    2. Intersect paths with effective capabilities (requested minus prohibited)
       to produce a capability-to-path-set map
    3. Collapse containment-redundant paths within each capability bucket
    4. Wrap each capability's path list in its typed enforcement model

    The intersect_fn and collapse_fn are injected from path_operations via the
    L3 orchestrator, avoiding a direct Composed->Composed cross-module import.
    """
    read_paths = extract_read_paths(security.security_paths)
    write_paths = extract_write_paths(security.security_paths)
    requested = extract_requested(security.security_capabilities)
    prohibited = extract_prohibited(security.security_capabilities)
    raw_grants = intersect_fn(read_paths, write_paths, requested, prohibited)
    collapsed = collapse_fn(raw_grants)
    fields = {capability: wrap_capability_paths(capability, capability_paths) for capability, capability_paths in collapsed.items()}
    return EnforcementExplicitGrants(**fields)
