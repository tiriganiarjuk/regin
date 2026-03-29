"""Tool resolution simple functions — path formatting and field matching.

CC=1-3 functions. No cross-module imports.

Predicate functions for tool registry matching and path display formatting.
The field_matches functions implement the "None spec = match any" unification
rule: when the agent definition doesn't specify a field (None), it matches
any registry entry value. This allows registry entries to serve as defaults
for unspecified fields.
"""


def relativize_path(abs_path: str, workspace_prefix: str) -> str:
    """Strip workspace prefix from path, returning relative or absolute."""
    if abs_path.startswith(workspace_prefix):
        return "./" + abs_path[len(workspace_prefix):]
    return abs_path


def field_matches(spec_value: str | None, entry_value: str) -> bool:
    """The "None = match any" rule for required entry fields.

    When the spec field is absent (None), the match succeeds regardless of
    the entry's value — an agent that doesn't specify write_frequency will
    match registry entries with any write_frequency. When present, must
    exactly equal the entry value.
    """
    return spec_value is None or spec_value == entry_value


def field_matches_present(spec_value: str | None, entry_value: str | None) -> bool:
    """Stricter match: both spec and entry must be present for a positive match.

    Used for file_path and directory_path where a present spec should only
    match a present entry — a spec with a file_path should not match a
    registry entry that only has a directory_path. None spec still matches
    anything (the "match any" rule).
    """
    if spec_value is None:
        return True
    return entry_value is not None and spec_value == entry_value
