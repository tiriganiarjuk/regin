"""Tree mutation simple functions — pattern-matched write-back.

CC=1-3 functions. Import from primitive only.

Handles both structural match cases for writing replacement values back to
the model tree: FoundInField (value is a named attribute on a BaseModel parent)
and FoundInList (value is an indexed item in a RootModel list). This is the
generic replacement operation used by include_expand.
"""

from regin.structure.model.found_item import FoundInField, FoundInList, FoundItem


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
