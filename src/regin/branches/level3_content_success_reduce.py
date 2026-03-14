"""Level 3 — Reduce success and failure criteria includes to inline items.

Gate in:  gate_paths_verified_input (reads paths-verified TOML, returns JSON)
Gate out: gate_success_reduced_output (validates JSON, writes TOML)
Delta:    Replace IncludeSuccessCriteria and IncludeFailureCriteria with loaded items.
          Two passes on separate lists within criteria.
"""

from pathlib import Path

from regin.functions.impure.gates import call_input_gate, call_output_gate
from regin.functions.impure.include_resolve import (
    resolve_failure_criteria_include,
    resolve_success_criteria_include,
)
from regin.functions.impure.model_mutate import walk_find_replace
from regin.structures.schema.agent_paths_resolved import (
    AgentPathsResolved,
    IncludeFailureCriteria,
    IncludeSuccessCriteria,
)
from regin.structures.schema.agent_success_reduced import AgentSuccessReduced


def run(input_path: Path, output_path: Path) -> str:
    """Execute the L3 success/failure reduce branch. Returns output JSON."""
    json_in = call_input_gate("gate_paths_verified_input", input_path)
    definition = AgentPathsResolved.model_validate_json(json_in)
    walk_find_replace(
        definition.criteria.success_criteria,
        IncludeSuccessCriteria,
        resolve_success_criteria_include,
    )
    walk_find_replace(
        definition.criteria.failure_criteria,
        IncludeFailureCriteria,
        resolve_failure_criteria_include,
    )
    json_mutated = definition.model_dump_json(by_alias=True, exclude_none=True)
    reduced = AgentSuccessReduced.model_validate_json(json_mutated)
    json_out = reduced.model_dump_json(by_alias=True, exclude_none=True)
    call_output_gate("gate_success_reduced_output", json_out, output_path)
    return json_out
