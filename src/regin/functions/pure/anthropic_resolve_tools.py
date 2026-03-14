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


def compose_invocation(binary_name: str, name_needed: bool) -> str:
    """Compose the bash heredoc invocation display."""
    if name_needed:
        return f"cat <<'EOF' | {binary_name} --name {{name}}\n{{json_data}}\nEOF"
    return f"cat <<'EOF' | {binary_name}\n{{json_data}}\nEOF"


def discover_tool(
    writing_output: WritingOutput | None,
    registry: list[ToolRegistryEntry],
) -> ResolvedTool | None:
    """Match enforcement spec against registry. Returns None when no match."""
    if writing_output is None:
        return None
    for entry in registry:
        if matches_registry(writing_output, entry):
            name_needed = (
                writing_output.writing_output.output_tool_name_needed is not None
                and writing_output.writing_output.output_tool_name_needed.root.root is True
            )
            variant = "with-name" if name_needed else "no-name"
            return ResolvedTool(
                tool_name=entry.binary_name,
                invocation_variant=variant,
                invocation_display=compose_invocation(entry.binary_name, name_needed),
            )
    return None
