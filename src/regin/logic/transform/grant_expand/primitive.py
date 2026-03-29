"""Grant expansion primitives — sort keys for deterministic output.

CC=1 functions. No branches, no iteration. No cross-module dependencies.

Sort keys that ensure grant entries are ordered by tool/command name.
Deterministic ordering matters for: TOML checkpoint diffs (identical inputs
always produce identical output order), test snapshot comparison, and
human readability of the rendered hooks config.
"""

from regin.structure.gen.schema.agent_anthropic_render import (
    CommandNameUnix,
    ToolNameAnthropic,
)


def by_tool_name(pair: tuple[ToolNameAnthropic, set[str]]) -> str:
    """Sort key for tool accumulator items."""
    return pair[0].value


def by_command_name(pair: tuple[CommandNameUnix, set[str]]) -> str:
    """Sort key for command accumulator items."""
    return pair[0].value
