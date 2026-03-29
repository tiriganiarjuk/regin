"""Tree mutation simple functions — pattern-matched write-back and DI contracts.

CC=1-3 functions. Import from primitive only.

Handles both structural match cases for writing replacement values back to
the model tree: FoundInField (value is a named attribute on a BaseModel parent)
and FoundInList (value is an indexed item in a RootModel list). This is the
generic replacement operation used by expand_replace.

Type aliases define the DI contracts for walk_find_replace in assembled.py:
- IncludeExpander: callback that loads an include file and mutates the tree
- TreeFinder: callback that locates all instances of a target type in the tree
"""

from collections.abc import Callable

from pydantic import BaseModel

from regin.structure.model.found_item import FoundInField, FoundInList, FoundItem

type IncludeExpander[T] = Callable[[FoundItem[T]], bool]
"""Loads an include file via a gate, converts it to the host schema, and
mutates the tree in place (splice, replace, or field-set). Returns True
on success. Implemented by resolve_*_include() in include_expand/assembled.
"""

type TreeFinder[T] = Callable[[BaseModel, type[T]], list[FoundItem[T]]]
"""Walks a Pydantic model tree depth-first and returns all instances of
the target type with their location metadata (parent + field/index).
Implemented by walk_and_find() in pure/tree_walk/composed.
"""


def replace_found[T](found: FoundItem[T], replacement: T) -> bool:
    """Write a replacement value back to the exact location where it was found.

    Dispatches on the two FoundItem variants:
    - FoundInField: setattr to write back to the parent's named attribute
    - FoundInList: index assignment to write back to the parent's list

    Returns True unconditionally — like splice, the write always succeeds
    because validation happened upstream in the gate.
    """
    match found:
        case FoundInField(parent=parent, field_name=field_name):
            setattr(parent, field_name, replacement)
        case FoundInList(parent=parent, index=index):
            parent.root[index] = replacement
    return True
