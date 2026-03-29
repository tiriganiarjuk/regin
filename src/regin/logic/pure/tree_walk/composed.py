"""Walk a Pydantic model tree and collect all instances of a target type.

CC=4+. Two traversal modes (list items vs fields) extracted as composed functions.

Pure — read-only traversal, no mutation. All functions return values.

The walk is read-only — it collects location metadata (parent reference,
index or field name) but does not modify the tree. The FoundItem wrappers
carry enough context for tree_mutate to write back to the exact location
where the target was found.

Two traversal modes match the two Pydantic base classes:
  - RootModel with list root -> collect_from_list (scan by index)
  - BaseModel with named fields -> collect_from_fields (scan by field name)

Each collector returns (found, recurse) — targets found at this level, plus
child models to continue searching. This separation makes the walk a simple
stack-based loop.
"""

from pydantic import BaseModel, RootModel

from regin.structure.model.found_item import FoundInField, FoundInList, FoundItem


def collect_from_list[T](
    current: RootModel,
    target: type[T],
) -> tuple[list[FoundItem[T]], list[BaseModel]]:
    """Scan a RootModel's list root by index. Return (found, recurse).

    Each list item is either: a target (wrapped as FoundInList with parent
    reference and index for write-back), or a BaseModel child to recurse into.
    Non-model items (strings, ints) are skipped — they can't contain targets.
    """
    found: list[FoundItem[T]] = []
    recurse: list[BaseModel] = []
    for i, item in enumerate(current.root):
        if isinstance(item, target):
            found.append(FoundInList(value=item, parent=current, index=i))
        elif isinstance(item, BaseModel):
            recurse.append(item)
    return found, recurse


def collect_from_fields[T](
    current: BaseModel,
    target: type[T],
) -> tuple[list[FoundItem[T]], list[BaseModel]]:
    """Scan a BaseModel's named fields. Return (found, recurse).

    Each field value is either: a target (wrapped as FoundInField with parent
    reference and field name for setattr write-back), or a BaseModel child
    to recurse into. None fields and scalar values are skipped.
    """
    found: list[FoundItem[T]] = []
    recurse: list[BaseModel] = []
    for field_name, field_value in current:
        if isinstance(field_value, target):
            found.append(FoundInField(value=field_value, parent=current, field_name=field_name))
        elif isinstance(field_value, BaseModel):
            recurse.append(field_value)
    return found, recurse


def walk_and_find[T](section: BaseModel, target: type[T]) -> list[FoundItem[T]]:
    """Walk a model tree depth-first, return all target instances with locations.

    Stack-based traversal: start with the root section, pop a node, collect
    targets and children, push children for further processing. The returned
    FoundItem list carries enough location metadata for tree_mutate to write
    replacements back to each found position.
    """
    found: list[FoundItem[T]] = []
    stack: list[BaseModel] = [section]
    while stack:
        current = stack.pop()
        if isinstance(current, RootModel) and isinstance(current.root, list):
            items, recurse = collect_from_list(current, target)
        else:
            items, recurse = collect_from_fields(current, target)
        found.extend(items)
        stack.extend(recurse)
    return found
