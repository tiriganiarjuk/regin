"""Orchestrator — resolve universal render into anthropic render."""

from regin.structures.tool_registry import ToolRegistryEntry
from regin.structures.schema import agent_universal_render as render
from regin.structures.schema import agent_anthropic_render as anthr

from regin.functions.pure.anthropic_resolve_model import resolve_model
from regin.functions.pure.anthropic_resolve_tools import discover_tool
from regin.functions.pure.anthropic_resolve_grants import explode_explicit, explode_implicit
from regin.functions.pure.anthropic_resolve_display import build_display
from regin.functions.pure.anthropic_resolve_hooks import build_hooks
from regin.functions.pure.anthropic_resolve_compose import (
    compose_critical_rules,
    compose_frontmatter,
    compose_identity,
    compose_security_boundary,
    compose_writing_output,
)


def pass_through_section(
    source_section: render.BaseModel,
    target_type: type[anthr.BaseModel],
) -> anthr.BaseModel:
    """Round-trip a section from universal to anthropic types."""
    return target_type.model_validate_json(
        source_section.model_dump_json(by_alias=True)
    )


def pass_through_nullable(
    source_section: render.BaseModel | None,
    target_type: type[anthr.BaseModel],
) -> anthr.BaseModel | None:
    """Round-trip a nullable section. Returns None when source is None."""
    if source_section is None:
        return None
    return target_type.model_validate_json(
        source_section.model_dump_json(by_alias=True)
    )


def resolve_grants_and_hooks(
    source: render.AgentUniversalRender,
    output_tool_name: str | None,
) -> tuple[anthr.ToolPathEntries | None, anthr.DisplayEntries | None, anthr.HooksConfig]:
    """Steps 3-5: explode grants, build display, build hooks."""
    explicit_tools, explicit_commands = (
        explode_explicit(source.security_boundary.capabilities)
        if source.security_boundary and source.security_boundary.capabilities
        else (None, None)
    )
    implicit_tools, implicit_commands = (
        explode_implicit(source.implicit_grants.capabilities)
        if source.implicit_grants
        else (None, None)
    )
    workspace_path = (
        source.security_boundary.workspace_path.root
        if source.security_boundary else ""
    )
    display = build_display(explicit_tools, explicit_commands, workspace_path)
    hooks = build_hooks(
        explicit_tools, explicit_commands,
        implicit_tools, implicit_commands,
        output_tool_name,
    )
    return hooks.tool_entries, display, hooks


def resolve_anthropic(
    source: render.AgentUniversalRender,
    registry: list[ToolRegistryEntry],
) -> anthr.AgentAnthropicRender:
    """Orchestrate all 8 steps and assemble the final result."""
    model = resolve_model(source.identity.capability_tier)
    resolved_tool = discover_tool(source.writing_output, registry)
    output_tool_name = resolved_tool.tool_name if resolved_tool else None
    merged_tools, display, hooks = resolve_grants_and_hooks(source, output_tool_name)
    identity = compose_identity(source.identity, model)
    workspace_path = source.security_boundary.workspace_path.root if source.security_boundary else ""

    return anthr.AgentAnthropicRender(
        identity=identity,
        security_boundary=compose_security_boundary(display, workspace_path),
        input=pass_through_section(source.input, anthr.Input),
        output=pass_through_section(source.output, anthr.Output),
        writing_output=compose_writing_output(resolved_tool, source.writing_output),
        constraints=pass_through_nullable(source.constraints, anthr.Constraints),
        anti_patterns=pass_through_nullable(source.anti_patterns, anthr.AntiPatterns),
        success_criteria=pass_through_nullable(source.success_criteria, anthr.SuccessCriteria),
        failure_criteria=pass_through_nullable(source.failure_criteria, anthr.FailureCriteria),
        return_format=pass_through_section(source.return_format, anthr.ReturnFormat),
        dispatcher=pass_through_section(source.dispatcher, anthr.Dispatcher),
        instructions=pass_through_section(source.instructions, anthr.Instructions),
        examples=pass_through_nullable(source.examples, anthr.Examples),
        critical_rules=compose_critical_rules(resolved_tool, source.writing_output),
        frontmatter=compose_frontmatter(identity, model, hooks, merged_tools),
    )
