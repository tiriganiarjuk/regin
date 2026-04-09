"""Path predicates for security validation and grant operations.

CC=1-3 functions. Building blocks for both security validation (blocking
checks) and grant operations (containment collapse). These encode the
filesystem containment model: path A contains path B when B starts with
A's prefix.
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
