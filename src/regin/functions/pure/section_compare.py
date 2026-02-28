"""Verify named sections are identical between two JSON documents.

Used during merge steps to confirm that shared sections (indirect, task,
security) have not diverged between two branch outputs.
"""

import json

from regin.structures.errors import SectionMismatch


def verify_sections_match(
    left_json: str,
    right_json: str,
    section_names: list[str],
) -> str:
    """Compare named sections between two JSON strings. Raises SectionMismatch."""
    left = json.loads(left_json)
    right = json.loads(right_json)
    for name in section_names:
        if left.get(name) != right.get(name):
            msg = f"section '{name}' differs between merge inputs"
            raise SectionMismatch(msg)
    return "match"
