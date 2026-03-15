"""Regroup enforcement grant sections.

security_boundary: explicit grants displayed to the agent.
implicit_grants: system-derived grants for hook enforcement only.
writing_output: enforcement output tool spec (unresolved).

Pure — receives typed model, returns typed model. No IO.
"""

from regin.structures.schema.agent_universal_format import AgentUniversalFormat
from regin.structures.schema import agent_universal_render as render


def regroup_security_boundary(source: AgentUniversalFormat) -> render.SecurityBoundary:
    """Assemble security boundary from security.paths + enforcement.explicit_grants."""
    grants = source.enforcement.enforcement_explicit_grants
    has_grants = any([grants.read, grants.search, grants.inspect, grants.write, grants.edit, grants.append])
    if not has_grants:
        return render.SecurityBoundary(
            workspace_path=render.PathExistsAbsolute(source.security.security_paths.paths_workspace.root),
        )
    return render.SecurityBoundary(
        workspace_path=render.PathExistsAbsolute(source.security.security_paths.paths_workspace.root),
        capabilities=render.EnforcementExplicitGrants.model_validate_json(
            grants.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
        ),
    )


def regroup_implicit_grants(source: AgentUniversalFormat) -> render.ImplicitGrants | None:
    """Assemble implicit grants from enforcement.implicit_grants."""
    grants = source.enforcement.enforcement_implicit_grants
    has_grants = any([grants.read, grants.write, grants.edit])
    if not has_grants:
        return None
    return render.ImplicitGrants(
        capabilities=render.EnforcementImplicitGrants.model_validate_json(
            grants.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
        ),
    )


def regroup_writing_output(source: AgentUniversalFormat) -> render.WritingOutput | None:
    """Wrap enforcement output tool. None for text/markdown agents."""
    tool = source.enforcement.enforcement_output_tool
    if tool is None:
        return None
    return render.WritingOutput(
        writing_output=render.EnforcementOutputTool.model_validate_json(
            tool.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
        ),
    )
