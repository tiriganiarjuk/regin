"""Level 6 — Merge content and permissions branches into universal format.

Gate in:  gate_permissions_resolved_input (left), gate_includes_merged_input (right)
Gate out: gate_universal_format_output (validates JSON, writes TOML)
Delta:    Left has enforcement section from permissions resolution.
          Right has resolved execution and criteria from content branch.
          Copy right's execution and criteria into left.
"""

from pathlib import Path

import gate_includes_merged_input
import gate_permissions_resolved_input
import gate_universal_format_output

from regin.logic.impure.gates.simple import validate_input, validate_output
from regin.structure.gen.schema.agent_includes_merged import AgentIncludesMerged
from regin.structure.gen.schema.agent_permissions_resolved import (
    AgentPermissionsResolved,
    Criteria,
    Execution,
)
from regin.structure.gen.schema.agent_universal_format import AgentUniversalFormat


def run(left_path: Path, right_path: Path, output_path: Path) -> str:
    """Execute the L6 universal merge branch. Returns output JSON."""
    json_left = validate_input(gate_permissions_resolved_input, left_path)
    json_right = validate_input(gate_includes_merged_input, right_path)
    left = AgentPermissionsResolved.model_validate_json(json_left)
    right = AgentIncludesMerged.model_validate_json(json_right)
    left.execution = Execution.model_validate_json(
        right.execution.model_dump_json(by_alias=True)
    )
    left.criteria = Criteria.model_validate_json(
        right.criteria.model_dump_json(by_alias=True)
    )
    json_mutated = left.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    merged = AgentUniversalFormat.model_validate_json(json_mutated)
    json_out = merged.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    validate_output(gate_universal_format_output, json_out, output_path)
    return json_out
