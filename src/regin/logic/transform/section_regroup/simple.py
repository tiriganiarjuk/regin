"""Section regroup simple functions — null-safe assembly.

CC=1-3. Import from primitive only within this module.

Low-branch assembly functions for the domain-to-consumption regroup. These
handle cases where domain data needs null-checking, round-tripping through
a different model type, or conditional assembly based on data presence.

The security boundary, implicit grants, and writing output sections all have
meaningful None states that signal "this feature is not configured" — which
the renderer interprets as "omit this section from the prompt entirely."
"""

from pydantic import BaseModel

from regin.structure.gen.schema.agent_universal_format import AgentUniversalFormat, StringProse
from regin.structure.gen.schema.agent_universal_render import (
    EnforcementExplicitGrants as RenderEnforcementExplicitGrants,
    EnforcementImplicitGrants as RenderEnforcementImplicitGrants,
    EnforcementOutputTool as RenderEnforcementOutputTool,
    ImplicitGrants as RenderImplicitGrants,
    PathExistsAbsolute as RenderPathExistsAbsolute,
    SecurityBoundary as RenderSecurityBoundary,
    WritingOutput as RenderWritingOutput,
)


def wrap_nullable(
    source_field: BaseModel | None,
    wrapper_type: type[BaseModel],
    field_name: str,
    inner_type: type[BaseModel],
) -> BaseModel | None:
    """Generic null-safe round-trip wrapper for Optional domain fields.

    Many domain fields are Optional — when absent, the consumption section
    should also be absent (None), not an empty container. The JSON round-trip
    (dump -> validate) ensures Pydantic alias and serialization rules are
    honored across schema boundaries.

    Used for: constraints, anti_patterns, success_criteria, failure_criteria —
    sections that are simple 1:1 copies with Optional handling.
    """
    if source_field is None:
        return None
    inner = inner_type.model_validate_json(
        source_field.model_dump_json(by_alias=True)
    )
    return wrapper_type(**{field_name: inner})


def regroup_security_boundary(source: AgentUniversalFormat) -> RenderSecurityBoundary:
    """Assemble security boundary from security.paths + enforcement.explicit_grants.

    Two assembly paths based on grant presence. When no explicit grants exist
    (the agent has no path-capability permissions), the security boundary
    contains only the workspace path — signaling to the renderer that the
    agent operates in a restricted "workspace-only" mode. When grants exist,
    the full capabilities model is included with the detailed permission map.
    """
    grants = source.enforcement.enforcement_explicit_grants
    has_grants = any([grants.read, grants.search, grants.inspect, grants.write, grants.edit, grants.append])
    if not has_grants:
        return RenderSecurityBoundary(
            workspace_path=RenderPathExistsAbsolute(source.security.security_paths.paths_workspace.root),
        )
    return RenderSecurityBoundary(
        workspace_path=RenderPathExistsAbsolute(source.security.security_paths.paths_workspace.root),
        capabilities=RenderEnforcementExplicitGrants.model_validate_json(
            grants.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
        ),
    )


def regroup_implicit_grants(source: AgentUniversalFormat) -> RenderImplicitGrants | None:
    """Assemble implicit grants section. Returns None when no implicit grants exist.

    None signals downstream that the "Implicit Grants" prompt section should be
    omitted entirely rather than rendered as an empty section. An agent with no
    IO/schema/context declarations will have no implicit grants.
    """
    grants = source.enforcement.enforcement_implicit_grants
    has_grants = any([grants.read, grants.write, grants.edit])
    if not has_grants:
        return None
    return RenderImplicitGrants(
        capabilities=RenderEnforcementImplicitGrants.model_validate_json(
            grants.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
        ),
    )


def regroup_writing_output(source: AgentUniversalFormat) -> RenderWritingOutput | None:
    """Wrap enforcement output tool. None for text/markdown agents.

    Returns None when the output tool was set to None in L3 (text/markdown
    format or no output path). This None propagates through to the renderer
    and means "no Writing Output section in the prompt."
    """
    tool = source.enforcement.enforcement_output_tool
    if tool is None:
        return None
    return RenderWritingOutput(
        writing_output=RenderEnforcementOutputTool.model_validate_json(
            tool.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
        ),
    )


def guard_return_field(
    mode: str, allowed_modes: set[str], field: StringProse | None,
) -> StringProse | None:
    """Return field value only when the return_mode activates it.

    Each return_mode activates a different subset of return instruction fields:
    - "status" -> status_instruction only
    - "status-metrics" -> status + metrics
    - "metrics-output" -> metrics + output
    - "output" -> output_instruction only

    Fields not in the active set are forced to None even if the author provided
    a value, because including them would confuse the LLM about what to return.
    """
    if mode not in allowed_modes or field is None:
        return None
    return field


