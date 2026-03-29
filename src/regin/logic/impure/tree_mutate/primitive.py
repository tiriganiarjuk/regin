"""Tree mutation primitives — single-operation list splice.

CC=1 functions. No branches. No cross-module dependencies.

The fundamental list-level mutation for the include expansion pipeline.
Splice replaces one item at a known index with zero or more items, shifting
subsequent items. This is the impure counterpart to tree_walk's pure find
operations — tree_walk locates targets, tree_mutate writes back to those
locations.
"""

from pydantic import BaseModel

from regin.structure.model.found_item import FoundInList


def splice_found[T](found: FoundInList[T], items: list[BaseModel]) -> bool:
    """Replace one list item with N items via Python slice assignment.

    The slice assignment root[i:i+1] = items replaces exactly one element
    (the include reference at the found index) with the loaded items.
    The parent.root is a mutable list from a Pydantic RootModel.

    Returns True unconditionally — the splice always succeeds because
    validation failures are caught earlier in the gate.
    """
    found.parent.root[found.index : found.index + 1] = items
    return True
