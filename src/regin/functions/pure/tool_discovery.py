"""Step 2: Custom tool discovery.

Matches an agent's enforcement_output_tool spec against a registry
of deployed Nornir writer tools. Two outcomes:

1. MATCH — returns a ResolvedTool with binary name and invocation
2. No match — raises CustomToolNotFound with a ToolBuildRequest

No spec at all → returns None (agent has no output tool).
All functions are pure — the registry is passed in as frozen data.
"""

from regin.structures.errors import CustomToolNotFound
from regin.structures.resolved_tool import ResolvedTool, ToolBuildRequest
from regin.structures.tool_registry import (
    OutputPathKind,
    ToolRegistryEntry,
)
from regin.structures.universal_render import AgentUniversalRender, EnforcementOutputTool


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

def match_tool_spec(
    output_tool: EnforcementOutputTool,
    registry: tuple[ToolRegistryEntry, ...],
) -> ToolRegistryEntry | None:
    """Find a registry entry that matches the agent's output tool spec."""
    for entry in registry:
        if spec_matches_entry(output_tool, entry):
            return entry
    return None


def spec_matches_entry(
    spec: EnforcementOutputTool,
    entry: ToolRegistryEntry,
) -> bool:
    """Check whether an agent spec matches a registry entry."""
    if spec.enforcement_output_tool_format is None:
        return False
    if spec.enforcement_output_tool_format.value != entry.output_format.value:
        return False
    if spec.enforcement_output_tool_write_frequency is None:
        return False
    if spec.enforcement_output_tool_write_frequency.value != entry.write_frequency.value:
        return False
    if not schema_paths_match(spec, entry):
        return False
    return output_paths_match(spec, entry)


def schema_paths_match(
    spec: EnforcementOutputTool,
    entry: ToolRegistryEntry,
) -> bool:
    """Check schema path agreement between spec and registry entry."""
    if spec.enforcement_output_tool_schema_path is None:
        return False
    return spec.enforcement_output_tool_schema_path.root == entry.schema_path


def extract_pattern_suffix(pattern: str) -> str:
    """Extract the file suffix from a FilenameTemplate.

    '{uid}.summaries.jsonl' → '.summaries.jsonl'
    '{entry-id}.json' → '.json'
    """
    idx = pattern.find("}")
    if idx == -1:
        return ""
    return pattern[idx + 1:]


def registry_suffix(entry: ToolRegistryEntry) -> str:
    """Derive the expected filename suffix from a registry entry."""
    if entry.output_path_kind == OutputPathKind.directory_name:
        return f".{entry.name_extension}" if entry.name_extension else ""
    if entry.output_path_kind == OutputPathKind.directory_prefix:
        return entry.name_suffix or ""
    return ""


def output_paths_match(
    spec: EnforcementOutputTool,
    entry: ToolRegistryEntry,
) -> bool:
    """Check output path and naming pattern agreement."""
    if entry.output_path_kind == OutputPathKind.fixed_file:
        if spec.enforcement_output_tool_file_path is None:
            return False
        return spec.enforcement_output_tool_file_path.root == entry.file_path
    if spec.enforcement_output_tool_directory_path is None:
        return False
    if spec.enforcement_output_tool_directory_path.root != entry.directory_path:
        return False
    spec_pattern = spec.enforcement_output_tool_name_pattern
    if spec_pattern is None:
        return registry_suffix(entry) == ""
    return extract_pattern_suffix(spec_pattern.root) == registry_suffix(entry)


# ---------------------------------------------------------------------------
# Invocation composition
# ---------------------------------------------------------------------------

def compose_invocation_display(entry: ToolRegistryEntry) -> str:
    """Compose the bash heredoc invocation for a matched tool."""
    if entry.output_path_kind == OutputPathKind.fixed_file:
        return (
            f"cat <<'RECORD' | {entry.binary_name}\n"
            f"{{...json...}}\n"
            f"RECORD"
        )
    return (
        f"cat <<'RECORD' | {entry.binary_name} {{name}}\n"
        f"{{...json...}}\n"
        f"RECORD"
    )


def determine_invocation_variant(entry: ToolRegistryEntry) -> str:
    """Determine whether the tool needs a name argument."""
    if entry.output_path_kind == OutputPathKind.fixed_file:
        return "no-name"
    return "with-name"


# ---------------------------------------------------------------------------
# Build request composition
# ---------------------------------------------------------------------------

def compose_build_request(
    output_tool: EnforcementOutputTool,
    model: AgentUniversalRender,
) -> ToolBuildRequest:
    """Compose a Nornir build request from the unmatched spec."""
    return ToolBuildRequest(
        agent_name=model.dispatcher.agent_name.root,
        output_format=output_tool.enforcement_output_tool_format.value,
        write_frequency=output_tool.enforcement_output_tool_write_frequency.value,
        schema_path=output_tool.enforcement_output_tool_schema_path.root,
        file_path=(
            output_tool.enforcement_output_tool_file_path.root
            if output_tool.enforcement_output_tool_file_path else None
        ),
        directory_path=(
            output_tool.enforcement_output_tool_directory_path.root
            if output_tool.enforcement_output_tool_directory_path else None
        ),
        name_needed=(
            output_tool.enforcement_output_tool_name_needed.root
            if output_tool.enforcement_output_tool_name_needed else False
        ),
        batch_size=(
            output_tool.enforcement_output_tool_batch_size.root
            if output_tool.enforcement_output_tool_batch_size else None
        ),
    )


# ---------------------------------------------------------------------------
# Discovery entry point
# ---------------------------------------------------------------------------

def discover_custom_tool(
    output_tool: EnforcementOutputTool | None,
    registry: tuple[ToolRegistryEntry, ...],
    model: AgentUniversalRender | None = None,
) -> ResolvedTool | None:
    """Match enforcement_output_tool spec against deployed writer tools.

    Returns ResolvedTool on match, None when no spec.
    Raises CustomToolNotFound with build request when spec exists
    but no matching tool is deployed.
    """
    if output_tool is None:
        return None
    entry = match_tool_spec(output_tool, registry)
    if entry is None:
        build_request = compose_build_request(output_tool, model)
        raise CustomToolNotFound(
            f"No deployed writer matches spec for agent "
            f"'{build_request.agent_name}'. "
            f"Build request:\n{build_request.model_dump_json(indent=2)}"
        )
    return ResolvedTool(
        tool_name=entry.binary_name,
        invocation_variant=determine_invocation_variant(entry),
        invocation_display=compose_invocation_display(entry),
    )
