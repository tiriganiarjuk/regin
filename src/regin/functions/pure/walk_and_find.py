"""Walk a model section and collect all instances of a target type.

The foundational search primitive for the DAG pipeline. Scoped to a
section (security, execution, criteria), finds instances of a specific
type without knowing field names or structure. Stops recursing into
found instances — they are leaves.

Returns FoundItem instances carrying location context for replacement
via replace_found/splice_found in functions/impure/.

Pure — read-only traversal, no mutation.
"""

from pydantic import BaseModel, RootModel

from regin.structures.found_item import FoundInField, FoundInList, FoundItem


def walk_and_find[T](section: BaseModel, target: type[T]) -> list[FoundItem[T]]:
    """Walk a model section, return all instances of target type with location."""
    found: list[FoundItem[T]] = []
    if isinstance(section, RootModel) and isinstance(section.root, list):
        for i, item in enumerate(section.root):
            if isinstance(item, target):
                found.append(FoundInList(value=item, parent=section, index=i))
            elif isinstance(item, BaseModel):
                found.extend(walk_and_find(item, target))
        return found
    for field_name, field_value in section:
        if isinstance(field_value, target):
            found.append(FoundInField(value=field_value, parent=section, field_name=field_name))
        elif isinstance(field_value, BaseModel):
            found.extend(walk_and_find(field_value, target))
    return found
