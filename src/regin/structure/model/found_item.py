"""Location context for instances found by walk_and_find.

Two location types match the two access patterns in the model tree:
- FoundInField: direct attribute on a BaseModel parent
- FoundInList: item in a RootModel's list
"""

from pydantic import BaseModel, ConfigDict, RootModel


class FoundInField[T](BaseModel):
    """Target found as a direct field on a parent model."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    value: T
    parent: BaseModel
    field_name: str


class FoundInList[T](BaseModel):
    """Target found as an item in a RootModel list."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    value: T
    parent: RootModel
    index: int


type FoundItem[T] = FoundInField[T] | FoundInList[T]
