"""Tool resolution composed — model resolve, tool discovery, display building.

CC=4+. Imports from simple within this module.

The L8 pre-resolution pipeline has three functions:
1. resolve_model: map abstract capability tier to concrete Anthropic model name
2. discover_tool: match the enforcement output tool spec against the tool
   registry to find the binary that will handle the agent's file output
3. build_display: collapse tool/command grant entries into a human-readable
   summary for the security boundary display in the rendered prompt

Pure — receives typed data, returns typed data. No IO (registry loading
happens in impure/registry, results are passed in).
"""

from regin.structure.model.resolved_tool import ResolvedTool
from regin.structure.config.tool_registry import ToolRegistryEntry
from regin.logic.pure.tool_resolve.simple import (
    field_matches,
    field_matches_present,
    relativize_path,
)
from regin.structure.gen.schema.agent_universal_render import AgentCapabilityTier, WritingOutput
from regin.structure.gen.schema.agent_anthropic_render import (
    AnthropicModel,
    CommandPathEntries,
    DisplayEntries,
    DisplayEntry,
    DisplayPath,
    DisplayToolCommand,
    DisplayToolsCommands,
    PathRelative,
    ToolPathEntries,
)


def resolve_model(tier: AgentCapabilityTier) -> AnthropicModel:
    """Map capability tier to Anthropic model name."""
    match tier:
        case AgentCapabilityTier.fast_cheap:
            return AnthropicModel.haiku
        case AgentCapabilityTier.standard | AgentCapabilityTier.analytical:
            return AnthropicModel.sonnet
        case AgentCapabilityTier.complex_reasoning | AgentCapabilityTier.max_capability:
            return AnthropicModel.opus
        case AgentCapabilityTier.inherit:
            return AnthropicModel.inherit


def matches_registry(writing_output: WritingOutput, entry: ToolRegistryEntry) -> bool:
    """Check if an enforcement output tool spec matches a registry entry.

    Requires exact format match (json/jsonl) plus soft matching on all other
    fields via the field_matches/field_matches_present predicates. The all([])
    clause is a conjunction: every field must match for the overall match to
    succeed. Linear scan through the registry — first match wins.
    """
    tool = writing_output.writing_output
    if tool.output_tool_format is None:
        return False
    if tool.output_tool_format.value != entry.output_format.value:
        return False
    return all([
        field_matches(
            tool.output_tool_write_frequency.value if tool.output_tool_write_frequency else None,
            entry.write_frequency.value,
        ),
        field_matches(
            tool.output_tool_schema_path.root if tool.output_tool_schema_path else None,
            entry.schema_path,
        ),
        field_matches_present(
            tool.output_tool_file_path.root if tool.output_tool_file_path else None,
            entry.file_path,
        ),
        field_matches_present(
            tool.output_tool_directory_path.root if tool.output_tool_directory_path else None,
            entry.directory_path,
        ),
    ])


def discover_tool(
    writing_output: WritingOutput | None,
    registry: list[ToolRegistryEntry],
) -> ResolvedTool | None:
    """Match enforcement spec against tool registry. Returns first match or None.

    Returns None in two cases: (1) writing_output is None (no output tool needed),
    (2) no registry entry matches (the agent's output spec doesn't correspond to
    any known tool binary).

    The output_path_kind determines the invocation variant: "fixed_file" means the
    output path is known at definition time (variant "no-name"), anything else means
    the agent must determine the filename at runtime (variant "with-name").
    """
    if writing_output is None:
        return None
    for entry in registry:
        if matches_registry(writing_output, entry):
            name_needed = entry.output_path_kind.value != "fixed_file"
            variant = "with-name" if name_needed else "no-name"
            return ResolvedTool(
                tool_name=entry.binary_name,
                invocation_variant=variant,
                invocation_display=entry.invocation,
            )
    return None


def collect_display_paths(
    tool_entries: ToolPathEntries | None,
    command_entries: CommandPathEntries | None,
) -> dict[str, list[str]]:
    """Accumulate tool/command names per absolute path."""
    path_to_tools: dict[str, list[str]] = {}
    if tool_entries is not None:
        for entry in tool_entries.root:
            for path in entry.paths.root:
                path_to_tools.setdefault(path.root, []).append(entry.tool.value)
    if command_entries is not None:
        for entry in command_entries.root:
            for path in entry.paths.root:
                path_to_tools.setdefault(path.root, []).append(entry.command.value)
    return path_to_tools


def build_display(
    tool_entries: ToolPathEntries | None,
    command_entries: CommandPathEntries | None,
    workspace_path: str,
) -> DisplayEntries | None:
    """Collapse tool/command grant entries into display entries grouped by path.

    The display is a human-readable summary that appears in the rendered prompt's
    security boundary section. Each entry shows a path and the tools/commands
    available on it. Paths within the workspace are relativized to ./ for
    readability; paths outside the workspace keep their absolute form.
    """
    path_to_tools = collect_display_paths(tool_entries, command_entries)
    if not path_to_tools:
        return None

    workspace_prefix = workspace_path.rstrip("/") + "/"
    items = []
    for abs_path in sorted(path_to_tools):
        rel_path = relativize_path(abs_path, workspace_prefix)
        tools_commands = sorted(set(path_to_tools[abs_path]))
        display_path = PathRelative(rel_path) if rel_path.startswith("./") else rel_path
        items.append(
            DisplayEntry(
                path=DisplayPath(display_path),
                tools=DisplayToolsCommands([DisplayToolCommand(name) for name in tools_commands]),
            )
        )
    return DisplayEntries(items)
