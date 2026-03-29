"""Grant expansion simple functions — type builders and accumulators.

CC=1-3 functions. Import from primitive only.

Type builders and accumulator functions for the grant expansion pipeline.
These bridge the gap between the capability-oriented grant model
(capability -> paths) and the tool-oriented hooks model (tool -> paths).

The accumulator functions merge entries from multiple sources (explicit +
implicit) using set union on paths, ensuring that a tool granted the same
path from both explicit and implicit sources gets a single deduplicated entry.
"""

from collections.abc import Iterator

from regin.structure.gen.schema.agent_anthropic_render import (
    CommandNameUnix,
    CommandPathEntry,
    CommandPathEntries,
    HooksConfig,
    OutputToolName,
    PathAbsolute,
    PathPrefixes,
    ToolNameAnthropic,
    ToolPathEntry,
    ToolPathEntries,
)
from regin.structure.gen.schema.agent_universal_render import PathExistsAbsolute
from regin.structure.model.grant_entries import GrantEntries

from regin.logic.transform.grant_expand.primitive import by_command_name, by_tool_name


def extract_paths(typed_paths: list[PathExistsAbsolute]) -> list[str]:
    """Extract raw path strings from a typed path list."""
    return [path.root for path in typed_paths]


def build_path_prefixes(path_set: set[str]) -> PathPrefixes:
    """Sort and wrap raw path strings into typed PathPrefixes."""
    return PathPrefixes([PathAbsolute(path) for path in sorted(path_set)])


def merge_into_tools(
    tool_mapping: dict[ToolNameAnthropic, set[str]],
) -> ToolPathEntries | None:
    """Convert tool-to-paths mapping into typed entries, sorted by tool name."""
    if not tool_mapping:
        return None
    items = [
        ToolPathEntry(tool=tool, paths=build_path_prefixes(path_set))
        for tool, path_set in sorted(tool_mapping.items(), key=by_tool_name)
    ]
    return ToolPathEntries(items)


def merge_into_commands(
    command_mapping: dict[CommandNameUnix, set[str]],
) -> CommandPathEntries | None:
    """Convert command-to-paths mapping into typed entries, sorted by name."""
    if not command_mapping:
        return None
    items = [
        CommandPathEntry(command=command, paths=build_path_prefixes(path_set))
        for command, path_set in sorted(command_mapping.items(), key=by_command_name)
    ]
    return CommandPathEntries(items)


def flatten_entries(
    *sources: ToolPathEntries | CommandPathEntries | None,
) -> Iterator[ToolPathEntry | CommandPathEntry]:
    """Yield all entries from non-None sources, filtering None."""
    for entries in sources:
        if entries is not None:
            yield from entries.root


def accumulate_entries(
    key_attr: str,
    *sources: ToolPathEntries | CommandPathEntries | None,
) -> dict[ToolNameAnthropic | CommandNameUnix, set[str]]:
    """Accumulate key->paths from multiple entry lists, unioning paths per key."""
    accumulated_paths: dict[ToolNameAnthropic | CommandNameUnix, set[str]] = {}
    for entry in flatten_entries(*sources):
        accumulated_paths.setdefault(getattr(entry, key_attr), set()).update(
            path.root for path in entry.paths.root
        )
    return accumulated_paths


def build_hooks(
    entries: GrantEntries,
    output_tool_name: str | None,
) -> HooksConfig:
    """Merge explicit + implicit grants and assemble the final HooksConfig.

    HooksConfig is the output of grant expansion — it tells the Anthropic
    runtime which tools/commands are allowed on which paths, and optionally
    which output tool to use. The output_tool field enables the special hooks
    that intercept the agent's file writes and validate them against the
    output spec.
    """
    return HooksConfig(
        output_tool=OutputToolName(output_tool_name) if output_tool_name else None,
        tool_entries=merge_into_tools(accumulate_entries("tool", entries.explicit_tools, entries.implicit_tools)),
        command_entries=merge_into_commands(accumulate_entries("command", entries.explicit_commands, entries.implicit_commands)),
    )
