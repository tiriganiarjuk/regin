"""Level 5 — Merge execution and criteria into fully-resolved includes.

Gate in:  gate_execution_merged_input (left), gate_criteria_merged_input (right)
Gate out: gate_includes_merged_output (validates JSON, writes TOML)
Delta:    Left has resolved execution (instructions + examples), right has resolved
          criteria (guardrails + success/failure). Copy right's criteria into left,
          serialize through output gate.
"""

from pathlib import Path

from regin.functions.impure.gates import call_input_gate, call_output_gate
from regin.structures.schema.agent_criteria_merged import AgentCriteriaMerged
from regin.structures.schema.agent_execution_merged import AgentExecutionMerged, Criteria
from regin.structures.schema.agent_includes_merged import AgentIncludesMerged


def run(left_path: Path, right_path: Path, output_path: Path) -> str:
    """Execute the L5 includes merge branch. Returns output JSON."""
    json_left = call_input_gate("gate_execution_merged_input", left_path)
    json_right = call_input_gate("gate_criteria_merged_input", right_path)
    left = AgentExecutionMerged.model_validate_json(json_left)
    right = AgentCriteriaMerged.model_validate_json(json_right)
    left.criteria = Criteria.model_validate_json(
        right.criteria.model_dump_json()
    )
    json_mutated = left.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    merged = AgentIncludesMerged.model_validate_json(json_mutated)
    json_out = merged.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    call_output_gate("gate_includes_merged_output", json_out, output_path)
    return json_out
