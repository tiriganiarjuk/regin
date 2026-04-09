"""Grant derive assembled — explicit and implicit grant derivation.

CC=1-2. Imports from composed (L4), simple (L2), and dispatch (L3).

Two entry points for the two grant derivation paths:
- derive_explicit_grants: intersection of author-declared paths with
  requested capabilities (the "positive permission" path)
- derive_implicit_grants: inference of minimum permissions from IO,
  schema, and context declarations
"""

from regin.logic.pure.grant_derive.composed import (
    collect_context_reads,
    collect_io_reads,
    collect_schema_reads,
    extract_prohibited,
)
from regin.logic.pure.grant_derive.dispatch import CAPABILITY_MODELS
from regin.logic.pure.grant_derive.simple import (
    build_raw_grants,
    collect_implicit_writes,
    extract_read_paths,
    extract_requested,
    extract_write_paths,
    wrap_implicit_edit,
    wrap_implicit_read,
    wrap_implicit_write,
)
from regin.logic.pure.path_operations.composed import (
    collapse_path_containment,
    intersect_paths_capabilities,
)
from regin.structure.gen.schema.agent_paths_resolved import Security
from regin.structure.gen.schema.agent_permissions_resolved import (
    EnforcementExplicitGrants,
    EnforcementImplicitGrants,
)


def derive_explicit_grants(
    security: Security,
) -> EnforcementExplicitGrants:
    """Run the full explicit grant derivation pipeline.

    Pipeline steps:
    1. Extract raw paths (read, write) and capability sets (requested, prohibited)
    2. Intersect paths with effective capabilities (requested minus prohibited)
    3. Collapse containment-redundant paths within each capability bucket
    4. Wrap each capability's path list in its typed enforcement model
    """
    read_paths = extract_read_paths(security.security_paths)
    write_paths = extract_write_paths(security.security_paths)
    requested = extract_requested(security.security_capabilities)
    prohibited = extract_prohibited(security.security_capabilities)
    raw_grants = intersect_paths_capabilities(read_paths, write_paths, requested, prohibited)
    collapsed = collapse_path_containment(raw_grants)
    fields = {capability: CAPABILITY_MODELS[capability](paths) for capability, paths in collapsed.items()}
    return EnforcementExplicitGrants(**fields)


def derive_implicit_grants(
    security: Security,
) -> EnforcementImplicitGrants:
    """Collect implicit sources, collapse paths, wrap in typed grant models.

    Implicit grants are inferred from IO, schema, and context declarations —
    the minimum permissions the agent needs to function, separate from what
    it explicitly requested. No search, inspect, or append — those require
    explicit capability requests.
    """
    workspace_name = security.security_paths.paths_workspace.root.rstrip("/").rsplit("/", 1)[-1]
    reads = (
        collect_io_reads(security.security_io, workspace_name)
        | collect_schema_reads(security.security_schema)
        | (collect_context_reads(security.context) if security.context else set())
    )
    writes = collect_implicit_writes(security.security_io, workspace_name)
    raw_grants = build_raw_grants(reads, writes)
    collapsed = collapse_path_containment(raw_grants)
    return EnforcementImplicitGrants(
        read=wrap_implicit_read(collapsed),
        write=wrap_implicit_write(collapsed),
        edit=wrap_implicit_edit(collapsed),
    )
