"""Path operations for security grant and blocking computation.

Predicates: is_subpath, paths_overlap.
intersect_paths_capabilities: cross paths with effective capability sets.
collapse_path_containment: deduplicate paths within each capability bucket.

Pure — operates on plain sets and lists, no IO.
"""

from regin.structures.schema.agent_paths_resolved import Capabilities

READ_POSSIBLE = frozenset({Capabilities.read, Capabilities.search, Capabilities.inspect})
WRITE_POSSIBLE = frozenset({
    Capabilities.read,
    Capabilities.search,
    Capabilities.inspect,
    Capabilities.write,
    Capabilities.edit,
    Capabilities.append,
})


def is_subpath(child: str, parent: str) -> bool:
    """True when child is strictly inside parent (not equal)."""
    return child.startswith(parent) and child != parent


def paths_overlap(left: str, right: str) -> bool:
    """True when either path contains the other, or they are equal."""
    return left == right or left.startswith(right) or right.startswith(left)


def intersect_paths_capabilities(
    read_paths: list[str],
    write_paths: list[str],
    requested: set[Capabilities],
    prohibited: set[Capabilities],
) -> dict[str, set[str]]:
    """Cross paths with effective capability sets to produce grant map."""
    grants: dict[str, set[str]] = {}
    effective_read = READ_POSSIBLE & requested - prohibited
    effective_write = WRITE_POSSIBLE & requested - prohibited
    for path in read_paths:
        for cap in effective_read:
            grants.setdefault(cap.value, set()).add(path)
    for path in write_paths:
        for cap in effective_write:
            grants.setdefault(cap.value, set()).add(path)
    return grants


def collapse_path_containment(grants: dict[str, set[str]]) -> dict[str, list[str]]:
    """Deduplicate paths within each capability bucket by containment."""
    result: dict[str, list[str]] = {}
    for cap, path_set in grants.items():
        sorted_paths = sorted(path_set, key=len)
        kept: list[str] = []
        for path in sorted_paths:
            absorbed = any(is_subpath(path, ancestor) for ancestor in kept)
            if not absorbed:
                kept.append(path)
        if kept:
            result[cap] = kept
    return result
