"""Step 4 — Build security boundary display entries."""

from regin.structures.schema.agent_anthropic_render import (
    DisplayEntries,
    DisplayEntry,
    DisplayPath,
    DisplayToolCommand,
    DisplayToolsCommands,
    PathRelative,
    ToolPathEntries,
    CommandPathEntries,
)


def collect_display_paths(
    tool_entries: ToolPathEntries | None,
    command_entries: CommandPathEntries | None,
) -> dict[str, list[str]]:
    """Accumulate tool/command names per absolute path."""
    path_acc: dict[str, list[str]] = {}
    if tool_entries is not None:
        for entry in tool_entries.root:
            for path in entry.paths.root:
                path_acc.setdefault(path.root, []).append(entry.tool.value)
    if command_entries is not None:
        for entry in command_entries.root:
            for path in entry.paths.root:
                path_acc.setdefault(path.root, []).append(entry.command.value)
    return path_acc


def relativize_path(abs_path: str, workspace_prefix: str) -> str:
    """Strip workspace prefix from path, returning relative or absolute."""
    if abs_path.startswith(workspace_prefix):
        return "./" + abs_path[len(workspace_prefix):]
    return abs_path


def build_display(
    tool_entries: ToolPathEntries | None,
    command_entries: CommandPathEntries | None,
    workspace_path: str,
) -> DisplayEntries | None:
    """Collapse tool/command path entries into display entries grouped by path."""
    path_acc = collect_display_paths(tool_entries, command_entries)
    if not path_acc:
        return None

    workspace_prefix = workspace_path.rstrip("/") + "/"
    items = []
    for abs_path in sorted(path_acc):
        rel_path = relativize_path(abs_path, workspace_prefix)
        tools_commands = sorted(set(path_acc[abs_path]))
        display_path = PathRelative(rel_path) if rel_path.startswith("./") else rel_path
        items.append(
            DisplayEntry(
                path=DisplayPath(display_path),
                tools=DisplayToolsCommands([DisplayToolCommand(tc) for tc in tools_commands]),
            )
        )
    return DisplayEntries(items)
