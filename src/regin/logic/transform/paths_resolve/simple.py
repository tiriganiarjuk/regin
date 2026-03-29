"""Simple-level functions for path resolution transform.

Pure functions, CC 2-3 each. No IO.
"""

from pydantic import BaseModel, RootModel


def resolve_path(value: str, workspace: str) -> str:
    """Resolve ./relative to /workspace/relative. Absolute paths pass through."""
    if value.startswith("./"):
        return f"{workspace}/{value[2:]}"
    return value


def rootmodel_list_children(node: RootModel) -> list[BaseModel]:
    """Extract BaseModel children from a RootModel whose root is a list."""
    return [item for item in node.root if isinstance(item, BaseModel)]


def rootmodel_single_child(node: RootModel) -> list[BaseModel]:
    """Return root as single-element list if it's a BaseModel, else empty."""
    if isinstance(node.root, BaseModel):
        return [node.root]
    return []


def field_model_children(node: BaseModel) -> list[BaseModel]:
    """Extract field values that are BaseModel instances."""
    return [value for _name, value in node if isinstance(value, BaseModel)]
