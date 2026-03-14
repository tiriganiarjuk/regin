"""Step 5 — Build hooks config by merging explicit + implicit grants."""

from regin.structures.schema.agent_anthropic_render import (
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


def by_tool_value(pair: tuple[ToolNameAnthropic, set[str]]) -> str:
    """Sort key for tool merge items."""
    return pair[0].value


def by_command_value(pair: tuple[CommandNameUnix, set[str]]) -> str:
    """Sort key for command merge items."""
    return pair[0].value


def merge_tool_entries(
    explicit: ToolPathEntries | None,
    implicit: ToolPathEntries | None,
) -> ToolPathEntries | None:
    """Merge explicit and implicit tool entries, unioning paths per tool."""
    acc: dict[ToolNameAnthropic, set[str]] = {}
    for entries in (explicit, implicit):
        if entries is None:
            continue
        for entry in entries.root:
            acc.setdefault(entry.tool, set()).update(
                path.root for path in entry.paths.root
            )
    if not acc:
        return None
    items = [
        ToolPathEntry(
            tool=tool,
            paths=PathPrefixes([PathAbsolute(path) for path in sorted(path_set)]),
        )
        for tool, path_set in sorted(acc.items(), key=by_tool_value)
    ]
    return ToolPathEntries(items)


def merge_command_entries(
    explicit: CommandPathEntries | None,
    implicit: CommandPathEntries | None,
) -> CommandPathEntries | None:
    """Merge explicit and implicit command entries, unioning paths per command."""
    acc: dict[CommandNameUnix, set[str]] = {}
    for entries in (explicit, implicit):
        if entries is None:
            continue
        for entry in entries.root:
            acc.setdefault(entry.command, set()).update(
                path.root for path in entry.paths.root
            )
    if not acc:
        return None
    items = [
        CommandPathEntry(
            command=cmd,
            paths=PathPrefixes([PathAbsolute(path) for path in sorted(path_set)]),
        )
        for cmd, path_set in sorted(acc.items(), key=by_command_value)
    ]
    return CommandPathEntries(items)


def build_hooks(
    explicit_tools: ToolPathEntries | None,
    explicit_commands: CommandPathEntries | None,
    implicit_tools: ToolPathEntries | None,
    implicit_commands: CommandPathEntries | None,
    output_tool_name: str | None,
) -> HooksConfig:
    """Merge explicit + implicit grants and assemble HooksConfig."""
    return HooksConfig(
        output_tool=OutputToolName(output_tool_name) if output_tool_name else None,
        tool_entries=merge_tool_entries(explicit_tools, implicit_tools),
        command_entries=merge_command_entries(explicit_commands, implicit_commands),
    )
