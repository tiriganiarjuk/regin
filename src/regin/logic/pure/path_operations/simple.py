"""Path predicates and DI type contracts for path operations.

CC=1-3 functions. Type aliases define the contracts for path_operations
functions that are injected via DI into grant_derive (avoiding
Composed→Composed cross-module imports).

Building blocks for both security validation (blocking checks) and grant
operations (containment collapse). These encode the filesystem containment
model: path A contains path B when B starts with A's prefix.
"""

from collections.abc import Callable

from regin.structure.gen.schema.agent_paths_resolved import Capabilities

type PathIntersector = Callable[
    [list[str], list[str], set[Capabilities], set[Capabilities]],
    dict[str, set[str]],
]
"""Crosses read/write paths with requested/prohibited capabilities.

Produces a capability-to-path-set map: {"read": {"/foo", "/bar"}, "write": {"/baz"}}.
Implemented by intersect_paths_capabilities() in path_operations/composed.
"""

type PathCollapser = Callable[
    [dict[str, set[str]]],
    dict[str, list[str]],
]
"""Deduplicates paths within each capability bucket by containment.

If /foo/ and /foo/bar/ are both granted, only /foo/ survives.
Implemented by collapse_path_containment() in path_operations/composed.
"""


def is_subpath(child: str, parent: str) -> bool:
    """Strict containment — child must begin with parent AND not equal it.

    The inequality matters for collapse: a path does not absorb itself.
    Used by collapse_path_containment and check_scratch_not_in_output.
    """
    return child.startswith(parent) and child != parent


def paths_overlap(left: str, right: str) -> bool:
    """Bidirectional containment check — the conflict predicate.

    Two paths "overlap" when either contains the other or they are identical.
    Used by blocking validation: overlapping paths in different permission
    domains (output vs allowed_write) create ambiguity that cannot be resolved.
    """
    return left == right or left.startswith(right) or right.startswith(left)
