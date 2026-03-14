"""Step 3 — Explode capability-keyed grants to tool-keyed and command-keyed."""

from regin.structures.schema.agent_anthropic_render import (
    CommandNameUnix,
    CommandPathEntry,
    CommandPathEntries,
    PathAbsolute,
    PathPrefixes,
    ToolNameAnthropic,
    ToolPathEntry,
    ToolPathEntries,
)
from regin.structures.schema.agent_universal_render import (
    EnforcementExplicitGrants,
    EnforcementImplicitGrants,
    PathExistsAbsolute,
)


def extract_paths(typed_paths: list[PathExistsAbsolute]) -> list[str]:
    """Extract raw path strings from a typed path list."""
    return [path.root for path in typed_paths]


def by_tool_name(pair: tuple[ToolNameAnthropic, set[str]]) -> str:
    """Sort key for tool accumulator items."""
    return pair[0].value


def by_command_name(pair: tuple[CommandNameUnix, set[str]]) -> str:
    """Sort key for command accumulator items."""
    return pair[0].value


def merge_into_tools(
    tool_mapping: dict[ToolNameAnthropic, set[str]],
) -> ToolPathEntries | None:
    """Convert tool-to-paths mapping into typed entries, sorted by tool name."""
    if not tool_mapping:
        return None
    items = [
        ToolPathEntry(
            tool=tool,
            paths=PathPrefixes([PathAbsolute(path) for path in sorted(path_set)]),
        )
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
        CommandPathEntry(
            command=command,
            paths=PathPrefixes([PathAbsolute(path) for path in sorted(path_set)]),
        )
        for command, path_set in sorted(command_mapping.items(), key=by_command_name)
    ]
    return CommandPathEntries(items)


def collect_explicit_tools(
    grants: EnforcementExplicitGrants,
) -> dict[ToolNameAnthropic, set[str]]:
    """Collect tool-to-paths from explicit grants (6 capabilities)."""
    result: dict[ToolNameAnthropic, set[str]] = {}
    if grants.read:
        paths = extract_paths(grants.read.root)
        result.setdefault(ToolNameAnthropic.Read, set()).update(paths)
    if grants.search:
        paths = extract_paths(grants.search.root)
        result.setdefault(ToolNameAnthropic.Grep, set()).update(paths)
        result.setdefault(ToolNameAnthropic.Glob, set()).update(paths)
    if grants.inspect:
        paths = extract_paths(grants.inspect.root)
        result.setdefault(ToolNameAnthropic.Read, set()).update(paths)
    if grants.write:
        result.setdefault(ToolNameAnthropic.Write, set()).update(
            extract_paths(grants.write.root)
        )
    if grants.edit:
        result.setdefault(ToolNameAnthropic.Edit, set()).update(
            extract_paths(grants.edit.root)
        )
    if grants.append:
        result.setdefault(ToolNameAnthropic.Edit, set()).update(
            extract_paths(grants.append.root)
        )
    return result


def collect_explicit_commands(
    grants: EnforcementExplicitGrants,
) -> dict[CommandNameUnix, set[str]]:
    """Collect command-to-paths from explicit grants."""
    result: dict[CommandNameUnix, set[str]] = {}
    if grants.search:
        paths = extract_paths(grants.search.root)
        result.setdefault(CommandNameUnix.find, set()).update(paths)
    if grants.inspect:
        paths = extract_paths(grants.inspect.root)
        for command in (CommandNameUnix.ls, CommandNameUnix.du, CommandNameUnix.wc,
                        CommandNameUnix.stat, CommandNameUnix.diff, CommandNameUnix.tree):
            result.setdefault(command, set()).update(paths)
    return result


def explode_explicit(
    grants: EnforcementExplicitGrants,
) -> tuple[ToolPathEntries | None, CommandPathEntries | None]:
    """Fan out explicit grants (6 capabilities) to tool/command entries."""
    return (
        merge_into_tools(collect_explicit_tools(grants)),
        merge_into_commands(collect_explicit_commands(grants)),
    )


def explode_implicit(
    grants: EnforcementImplicitGrants,
) -> tuple[ToolPathEntries | None, CommandPathEntries | None]:
    """Fan out implicit grants (3 capabilities) to tool entries only."""
    tool_mapping: dict[ToolNameAnthropic, set[str]] = {}
    if grants.read:
        tool_mapping.setdefault(ToolNameAnthropic.Read, set()).update(
            extract_paths(grants.read.root)
        )
    if grants.write:
        tool_mapping.setdefault(ToolNameAnthropic.Write, set()).update(
            extract_paths(grants.write.root)
        )
    if grants.edit:
        tool_mapping.setdefault(ToolNameAnthropic.Edit, set()).update(
            extract_paths(grants.edit.root)
        )
    return merge_into_tools(tool_mapping), None
