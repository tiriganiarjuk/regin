"""Level 3 — Reduce guardrails includes to inline constraints and anti-patterns.

Gate in:  gate_paths_verified_input (reads paths-verified TOML, returns JSON)
Gate out: gate_guardrails_reduced_output (validates JSON, writes TOML)
Delta:    Load IncludeGuardrailsConstraints and IncludeGuardrailsAntiPatterns into
          inline fields, clear include references.
"""

from pathlib import Path

from regin.functions.impure.gates import call_input_gate, call_output_gate
from regin.functions.impure.include_resolve import (
    resolve_guardrails_anti_patterns_include,
    resolve_guardrails_constraints_include,
)
from regin.functions.impure.model_mutate import walk_find_replace
from regin.structures.guardrails_reduced import AgentGuardrailsReduced
from regin.structures.paths_resolved import (
    AgentPathsResolved,
    IncludeGuardrailsAntiPatterns,
    IncludeGuardrailsConstraints,
)


def run(input_path: Path, output_path: Path) -> str:
    """Execute the L3 guardrails reduce branch. Returns output JSON."""
    json_in = call_input_gate("gate_paths_verified_input", input_path)
    definition = AgentPathsResolved.model_validate_json(json_in)
    if definition.criteria.guardrails:
        walk_find_replace(
            definition.criteria.guardrails,
            IncludeGuardrailsConstraints,
            resolve_guardrails_constraints_include,
        )
        walk_find_replace(
            definition.criteria.guardrails,
            IncludeGuardrailsAntiPatterns,
            resolve_guardrails_anti_patterns_include,
        )
    json_mutated = definition.model_dump_json(by_alias=True, exclude_none=True)
    reduced = AgentGuardrailsReduced.model_validate_json(json_mutated)
    json_out = reduced.model_dump_json(by_alias=True, exclude_none=True)
    call_output_gate("gate_guardrails_reduced_output", json_out, output_path)
    return json_out
