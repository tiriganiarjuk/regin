"""Level 3 — Reduce success and failure criteria includes to inline items.

Gate in:  gate_paths_verified_input (reads paths-verified TOML, returns JSON)
Gate out: gate_success_reduced_output (validates JSON, writes TOML)
Delta:    Replace IncludeSuccessCriteria and IncludeFailureCriteria with loaded items.
          Two passes on separate lists within criteria.
"""

from pathlib import Path

import gate_paths_verified_input
import gate_success_reduced_output

from regin.logic.impure.gates.simple import validate_input, validate_output
from regin.logic.impure.include_expand.assembled import (
    resolve_failure_criteria_include,
    resolve_success_criteria_include,
)
from regin.logic.impure.tree_mutate.assembled import walk_find_replace
from regin.logic.pure.tree_walk.composed import walk_and_find
from regin.structure.gen.schema.agent_paths_resolved import (
    AgentPathsResolved,
    IncludeFailureCriteria,
    IncludeSuccessCriteria,
)
from regin.structure.gen.schema.agent_success_reduced import AgentSuccessReduced


def run(input_path: Path, output_path: Path) -> str:
    """Execute the L3 success/failure reduce branch. Returns output JSON."""
    json_in = validate_input(gate_paths_verified_input, input_path)
    definition = AgentPathsResolved.model_validate_json(json_in)
    walk_find_replace(
        definition.criteria.success_criteria,
        IncludeSuccessCriteria,
        resolve_success_criteria_include,
        walk_and_find,
    )
    walk_find_replace(
        definition.criteria.failure_criteria,
        IncludeFailureCriteria,
        resolve_failure_criteria_include,
        walk_and_find,
    )
    json_mutated = definition.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    reduced = AgentSuccessReduced.model_validate_json(json_mutated)
    json_out = reduced.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    validate_output(gate_success_reduced_output, json_out, output_path)
    return json_out
