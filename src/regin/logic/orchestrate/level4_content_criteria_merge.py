"""Level 4 — Merge reduced guardrails and success/failure into criteria.

Gate in:  gate_guardrails_reduced_input (left), gate_success_reduced_input (right)
Gate out: gate_criteria_merged_output (validates JSON, writes TOML)
Delta:    Left has resolved guardrails, right has resolved success/failure.
          Copy right's success and failure criteria into left, serialize through output gate.
"""

from pathlib import Path

import gate_criteria_merged_output
import gate_guardrails_reduced_input
import gate_success_reduced_input

from regin.logic.impure.gates.simple import validate_input, validate_output
from regin.structure.gen.schema.agent_criteria_merged import AgentCriteriaMerged
from regin.structure.gen.schema.agent_guardrails_reduced import (
    AgentGuardrailsReduced,
    FailureCriteria,
    SuccessCriteria,
)
from regin.structure.gen.schema.agent_success_reduced import AgentSuccessReduced


def run(left_path: Path, right_path: Path, output_path: Path) -> str:
    """Execute the L4 criteria merge branch. Returns output JSON."""
    json_left = validate_input(gate_guardrails_reduced_input, left_path)
    json_right = validate_input(gate_success_reduced_input, right_path)
    left = AgentGuardrailsReduced.model_validate_json(json_left)
    right = AgentSuccessReduced.model_validate_json(json_right)
    left.criteria.success_criteria = SuccessCriteria.model_validate_json(
        right.criteria.success_criteria.model_dump_json()
    )
    left.criteria.failure_criteria = FailureCriteria.model_validate_json(
        right.criteria.failure_criteria.model_dump_json()
    )
    json_mutated = left.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    merged = AgentCriteriaMerged.model_validate_json(json_mutated)
    json_out = merged.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    validate_output(gate_criteria_merged_output, json_out, output_path)
    return json_out
