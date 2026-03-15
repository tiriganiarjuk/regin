"""Step 2 — Discover custom output tool from registry."""

from regin.structures.resolved_tool import ResolvedTool
from regin.structures.tool_registry import ToolRegistryEntry
from regin.structures.schema.agent_universal_render import WritingOutput


def matches_registry(spec: WritingOutput, entry: ToolRegistryEntry) -> bool:
    """Check if an enforcement spec matches a registry entry."""
    tool = spec.writing_output
    if tool.output_tool_format is None:
        return False
    if tool.output_tool_format.value != entry.output_format.value:
        return False
    if tool.output_tool_write_frequency is not None:
        if tool.output_tool_write_frequency.value != entry.write_frequency.value:
            return False
    if tool.output_tool_schema_path is not None:
        if tool.output_tool_schema_path.root != entry.schema_path:
            return False
    if tool.output_tool_file_path is not None:
        if entry.file_path is None or tool.output_tool_file_path.root != entry.file_path:
            return False
    if tool.output_tool_directory_path is not None:
        if entry.directory_path is None or tool.output_tool_directory_path.root != entry.directory_path:
            return False
    return True


def discover_tool(
    writing_output: WritingOutput | None,
    registry: list[ToolRegistryEntry],
) -> ResolvedTool | None:
    """Match enforcement spec against registry. Returns None when no match."""
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
