"""Resolve universal render into Anthropic platform format.

Gate in:  gate_universal_render_input (reads TOML, returns validated JSON)
Gate out: gate_anthropic_render_output (validates JSON, writes TOML)
Delta:    12 consumption sections -> 13 Anthropic sections.
          Model resolved, grants exploded, hooks built, frontmatter composed.
"""

from pathlib import Path

import gate_anthropic_render_output
import gate_universal_render_input

from regin.logic.impure.gates.simple import validate_input, validate_output
from regin.logic.impure.registry.simple import load_registry
from regin.logic.pure.tool_resolve.composed import (
    build_filesystem_permissions,
    discover_tool,
    resolve_model,
)
from regin.logic.transform.grant_expand.composed import resolve_grants_and_hooks
from regin.logic.transform.vendor_compose.assembled import compose_anthropic_sections
from regin.structure.config.registry_location import RegistryLocation
from regin.structure.gen.schema.agent_universal_render import AgentUniversalRender
from regin.structure.model.anthropic_context import AnthropicContext


def run(input_path: Path, output_path: Path) -> str:
    """Execute the anthropic resolve branch. Returns output JSON."""
    json_in = validate_input(gate_universal_render_input, input_path)
    source = AgentUniversalRender.model_validate_json(json_in)
    registry = load_registry(RegistryLocation())
    model = resolve_model(source.identity.capability_tier)
    resolved_tool = discover_tool(source.writing_output, registry)
    explicit_tools, explicit_commands, hooks = resolve_grants_and_hooks(source, resolved_tool)
    workspace = source.security_boundary.workspace_path.root if source.security_boundary else ""
    filesystem_permissions = build_filesystem_permissions(explicit_tools, explicit_commands, workspace)
    context = AnthropicContext(
        model=model, resolved_tool=resolved_tool,
        merged_tools=hooks.tool_entries, filesystem_permissions=filesystem_permissions, hooks=hooks,
    )
    result = compose_anthropic_sections(source, context)
    json_out = result.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    validate_output(gate_anthropic_render_output, json_out, output_path)
    return json_out
