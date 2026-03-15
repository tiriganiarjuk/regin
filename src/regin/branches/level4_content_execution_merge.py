"""Level 4 — Merge reduced instructions and examples into execution.

Gate in:  gate_instructions_reduced_input (left), gate_examples_reduced_input (right)
Gate out: gate_execution_merged_output (validates JSON, writes TOML)
Delta:    Left has resolved instructions, right has resolved examples.
          Copy right's examples into left, serialize through output gate.
"""

from pathlib import Path

from regin.functions.impure.gates import call_input_gate, call_output_gate
from regin.structures.schema.agent_examples_reduced import AgentExamplesReduced
from regin.structures.schema.agent_execution_merged import AgentExecutionMerged
from regin.structures.schema.agent_instructions_reduced import (
    AgentInstructionsReduced,
    ExecutionExamples,
)


def run(left_path: Path, right_path: Path, output_path: Path) -> str:
    """Execute the L4 execution merge branch. Returns output JSON."""
    json_left = call_input_gate("gate_instructions_reduced_input", left_path)
    json_right = call_input_gate("gate_examples_reduced_input", right_path)
    left = AgentInstructionsReduced.model_validate_json(json_left)
    right = AgentExamplesReduced.model_validate_json(json_right)
    left.execution.execution_examples = ExecutionExamples.model_validate_json(
        right.execution.execution_examples.model_dump_json()
    )
    json_mutated = left.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    merged = AgentExecutionMerged.model_validate_json(json_mutated)
    json_out = merged.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    call_output_gate("gate_execution_merged_output", json_out, output_path)
    return json_out
