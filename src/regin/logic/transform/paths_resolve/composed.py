"""Resolve workspace-relative paths to absolute in a raw definition model.

Stack-based walk: finds PathRelative and PathExistsRelative instances,
resolves ./relative to /workspace/relative. Returns serialized JSON
ready for AgentPathsResolved validation.

No IO. No BeforeValidator. No recursion. Every transform is explicit.
"""

from pydantic import BaseModel, RootModel

from regin.logic.transform.paths_resolve.simple import (
    field_model_children,
    resolve_path,
    rootmodel_list_children,
    rootmodel_single_child,
)
from regin.structure.gen.schema.agent_raw_definition import (
    AgentRawDefinition,
    PathExistsRelative,
    PathRelative,
)


def resolve_paths_in_model(model: AgentRawDefinition, workspace: str) -> str:
    """Walk model tree, resolve all relative paths, return JSON.

    Stack-based traversal finds PathRelative and PathExistsRelative
    RootModel instances and resolves their root values in place.
    Returns serialized JSON suitable for AgentPathsResolved validation.
    """
    stack: list[BaseModel] = [model]
    while stack:
        node = stack.pop()
        if isinstance(node, (PathRelative, PathExistsRelative)):
            node.root = resolve_path(node.root, workspace)
        elif isinstance(node, RootModel) and isinstance(node.root, list):
            stack.extend(rootmodel_list_children(node))
        elif isinstance(node, RootModel):
            stack.extend(rootmodel_single_child(node))
        else:
            stack.extend(field_model_children(node))

    return model.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
