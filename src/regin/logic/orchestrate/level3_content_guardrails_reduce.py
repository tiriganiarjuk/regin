"""Level 3 — Reduce guardrails includes to inline constraints and anti-patterns.

Gate in:  gate_paths_verified_input (reads paths-verified TOML, returns JSON)
Gate out: gate_guardrails_reduced_output (validates JSON, writes TOML)
Delta:    Load IncludeGuardrailsConstraints and IncludeGuardrailsAntiPatterns into
          inline fields, clear include references.
"""

from pathlib import Path

import gate_guardrails_reduced_output
import gate_paths_verified_input

from regin.logic.impure.gates.simple import validate_input, validate_output
from regin.logic.impure.include_expand.assembled import (
    resolve_guardrails_anti_patterns_include,
    resolve_guardrails_constraints_include,
)
from regin.logic.impure.tree_mutate.assembled import walk_find_replace
from regin.logic.pure.tree_walk.composed import walk_and_find
from regin.structure.gen.schema.agent_guardrails_reduced import AgentGuardrailsReduced
from regin.structure.gen.schema.agent_paths_resolved import (
    AgentPathsResolved,
    IncludeGuardrailsAntiPatterns,
    IncludeGuardrailsConstraints,
)


def run(input_path: Path, output_path: Path) -> str:
    """Execute the L3 guardrails reduce branch. Returns output JSON."""
    json_in = validate_input(gate_paths_verified_input, input_path)
    definition = AgentPathsResolved.model_validate_json(json_in)
    if definition.criteria.guardrails:
        walk_find_replace(
            definition.criteria.guardrails,
            IncludeGuardrailsConstraints,
            resolve_guardrails_constraints_include,
            walk_and_find,
        )
        walk_find_replace(
            definition.criteria.guardrails,
            IncludeGuardrailsAntiPatterns,
            resolve_guardrails_anti_patterns_include,
            walk_and_find,
        )
    json_mutated = definition.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    reduced = AgentGuardrailsReduced.model_validate_json(json_mutated)
    json_out = reduced.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    validate_output(gate_guardrails_reduced_output, json_out, output_path)
    return json_out
