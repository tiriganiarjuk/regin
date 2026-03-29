"""Path operations for security grant and blocking computation.

CC=4+. Imports from simple within this module.

The two key operations form a pipeline: intersect produces a capability-to-
path-set map that may contain redundant paths, then collapse deduplicates
by containment. The separation matters because intersection is
O(paths * capabilities) while collapse is O(paths^2) per capability —
they have different performance characteristics and are independently testable.

These functions are the core of the grant derivation math. They are injected
via DI into grant_derive/assembled and grant_derive/composed to avoid
cross-module Composed->Composed imports.
"""

from regin.structure.config.capability_tiers import PATH_CAPABILITY_TIERS
from regin.structure.gen.schema.agent_paths_resolved import Capabilities

from regin.logic.pure.path_operations.simple import is_subpath


def intersect_paths_capabilities(
    read_paths: list[str],
    write_paths: list[str],
    requested: set[Capabilities],
    prohibited: set[Capabilities],
) -> dict[str, set[str]]:
    """Cross paths with effective capability sets to produce the grant map.

    Each path is crossed with its tier's effective capabilities:
    - Read paths enable read-tier capabilities: {read, search, inspect}
    - Write paths enable ALL capabilities: {read, search, inspect, write, edit, append}
      (writing subsumes reading)

    "Effective" = (tier capabilities AND requested) MINUS prohibited.
    Note: & binds tighter than - in Python sets, so the expression
    reads as (tier & requested) - prohibited.
    """
    grants: dict[str, set[str]] = {}
    # Read-tier: capabilities that read paths enable (observe only)
    effective_read = PATH_CAPABILITY_TIERS.read & requested - prohibited
    # Write-tier: capabilities that write paths enable (observe + mutate)
    effective_write = PATH_CAPABILITY_TIERS.write & requested - prohibited
    for path in read_paths:
        for capability in effective_read:
            grants.setdefault(capability.value, set()).add(path)
    for path in write_paths:
        for capability in effective_write:
            grants.setdefault(capability.value, set()).add(path)
    return grants


def collapse_path_containment(grants: dict[str, set[str]]) -> dict[str, list[str]]:
    """Deduplicate paths within each capability bucket by containment.

    If /foo/ and /foo/bar/ are both granted for the same capability, only
    /foo/ survives because it already covers /foo/bar/. This reduces the
    grant model to its minimal permission set.

    Algorithm: sort paths by length (shortest first, since shorter paths are
    potential ancestors), then for each path check if any already-kept path
    is an ancestor. If so, the current path is "absorbed" — its permission
    is already covered. The kept list grows monotonically with non-contained
    paths.
    """
    result: dict[str, list[str]] = {}
    for capability, path_set in grants.items():
        sorted_paths = sorted(path_set, key=len)
        kept: list[str] = []
        for path in sorted_paths:
            absorbed = any(is_subpath(path, ancestor) for ancestor in kept)
            if not absorbed:
                kept.append(path)
        if kept:
            result[capability] = kept
    return result
