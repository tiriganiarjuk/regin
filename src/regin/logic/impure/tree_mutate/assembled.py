"""Tree mutation assembled — find-replace loop with injected search.

CC=1-2. DI: find_fn injected from caller to avoid cross-zone import.

The "find one, replace one" loop (rather than "find all, replace all") is
deliberate. Each replacement mutates the model tree, which may shift list
indices or change field values. Re-finding after each replacement ensures
the find_fn operates on the current tree state, not a stale snapshot.
This makes the algorithm correct for splice operations where list lengths
change.

The loop invariant: after each iteration, the model contains one fewer
instance of the target type than before. Termination is guaranteed because
each replace_fn call removes exactly one target instance.

The find_fn is injected via DI (rather than importing tree_walk/composed
directly) because tree_mutate is in the impure zone and tree_walk is in
the pure zone — the import would cross zone boundaries at the same level.
"""

from pydantic import BaseModel

from regin.logic.impure.tree_mutate.simple import IncludeExpander, TreeFinder


def walk_find_replace[T](
    section: BaseModel,
    target: type[T],
    replace_fn: IncludeExpander[T],
    find_fn: TreeFinder[T],
) -> bool:
    """Find-one-replace-one loop until no instances of target type remain.

    Each iteration: find the first target in the current tree state, replace
    it via the callback, then re-search the (now mutated) tree. This ensures
    correctness when splice operations change list lengths.

    Returns True if any replacements were made, False if the tree contained
    no instances of the target type.
    """
    replaced = False
    while found := find_fn(section, target):
        replace_fn(found[0])
        replaced = True
    return replaced
