"""Mutate a Pydantic model tree using location context from walk_and_find.

replace_found: 1:1 replacement (field-based includes, single items).
splice_found: 1:many replacement in lists (include expands to multiple items).
walk_find_replace: find-one-replace-one loop. Pure search, caller-supplied
                   replace function. Each iteration sees a fully updated model.

Impure — mutates the model in place. Gates validate at boundaries.
"""

from collections.abc import Callable

from pydantic import BaseModel

from regin.functions.pure.walk_and_find import walk_and_find
from regin.structures.found_item import FoundInField, FoundInList, FoundItem


def replace_found[T](found: FoundItem[T], replacement: T) -> bool:
    """Write a replacement value back to the location where it was found."""
    match found:
        case FoundInField(parent=parent, field_name=field_name):
            setattr(parent, field_name, replacement)
        case FoundInList(parent=parent, index=index):
            parent.root[index] = replacement
    return True


def splice_found[T](found: FoundInList[T], items: list[BaseModel]) -> bool:
    """Replace a single list item with multiple items (1:many expansion)."""
    found.parent.root[found.index : found.index + 1] = items
    return True


def walk_find_replace[T](
    section: BaseModel,
    target: type[T],
    replace_fn: Callable[[FoundItem[T]], bool],
) -> bool:
    """Find-one-replace-one loop until no targets remain.

    Each iteration works on a fully updated model.
    Returns True if any replacements were made.
    """
    replaced = False
    while found := walk_and_find(section, target):
        replace_fn(found[0])
        replaced = True
    return replaced
