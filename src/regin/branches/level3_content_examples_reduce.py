"""Level 3 — Reduce example includes to inline groups and entries.

Gate in:  gate_paths_verified_input (reads paths-verified TOML, returns JSON)
Gate out: gate_examples_reduced_output (validates JSON, writes TOML)
Delta:    Replace IncludeExampleGroup and IncludeExample references with loaded content.
          Two passes: groups first (1:1 replace), then entries within groups (splice).
"""

from pathlib import Path

from regin.functions.impure.gates import call_input_gate, call_output_gate
from regin.functions.impure.include_resolve import (
    resolve_example_entry_include,
    resolve_example_group_include,
)
from regin.functions.impure.model_mutate import walk_find_replace
from regin.structures.schema.agent_examples_reduced import AgentExamplesReduced
from regin.structures.schema.agent_paths_resolved import (
    AgentPathsResolved,
    IncludeExample,
    IncludeExampleGroup,
)


def run(input_path: Path, output_path: Path) -> str:
    """Execute the L3 examples reduce branch. Returns output JSON."""
    json_in = call_input_gate("gate_paths_verified_input", input_path)
    definition = AgentPathsResolved.model_validate_json(json_in)
    walk_find_replace(
        definition.execution.execution_examples,
        IncludeExampleGroup,
        resolve_example_group_include,
    )
    walk_find_replace(
        definition.execution.execution_examples,
        IncludeExample,
        resolve_example_entry_include,
    )
    json_mutated = definition.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    reduced = AgentExamplesReduced.model_validate_json(json_mutated)
    json_out = reduced.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    call_output_gate("gate_examples_reduced_output", json_out, output_path)
    return json_out
