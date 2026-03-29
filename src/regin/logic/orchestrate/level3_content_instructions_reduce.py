"""Level 3 — Reduce instruction includes to inline steps.

Gate in:  gate_paths_verified_input (reads paths-verified TOML, returns JSON)
Gate out: gate_instructions_reduced_output (validates JSON, writes TOML)
Delta:    Replace IncludeInstruction references with loaded InstructionStep content.
          walk_find_replace loop: find one include, gate-load the file, splice
          the loaded steps into the list, repeat until none remain.
"""

from pathlib import Path

import gate_instructions_reduced_output
import gate_paths_verified_input

from regin.logic.impure.gates.simple import validate_input, validate_output
from regin.logic.impure.include_expand.assembled import resolve_instruction_include
from regin.logic.impure.tree_mutate.assembled import walk_find_replace
from regin.logic.pure.tree_walk.composed import walk_and_find
from regin.structure.gen.schema.agent_instructions_reduced import AgentInstructionsReduced
from regin.structure.gen.schema.agent_paths_resolved import AgentPathsResolved, IncludeInstruction


def run(input_path: Path, output_path: Path) -> str:
    """Execute the L3 instructions reduce branch. Returns output JSON."""
    json_in = validate_input(gate_paths_verified_input, input_path)
    definition = AgentPathsResolved.model_validate_json(json_in)
    walk_find_replace(
        definition.execution.execution_instructions,
        IncludeInstruction,
        resolve_instruction_include,
        walk_and_find,
    )
    json_mutated = definition.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    reduced = AgentInstructionsReduced.model_validate_json(json_mutated)
    json_out = reduced.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    validate_output(gate_instructions_reduced_output, json_out, output_path)
    return json_out
