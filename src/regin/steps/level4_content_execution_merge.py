"""Level 4 — Merge instructions-reduced + examples-reduced.

Gate in: gate_instructions_reduced_input + gate_examples_reduced_input
Gate out: gate_execution_merged_output

Takes inlined instructions from one branch, inlined examples from the other.
"""

from regin.functions.impure.runner import run_merge
from regin.functions.pure.mergers import merge_execution


def run(instructions_path: str, examples_path: str, output_path: str) -> str:
    """Execute level 4: execution merge. Returns output path."""
    return run_merge(
        ["gate_instructions_reduced_input", "gate_examples_reduced_input"],
        "gate_execution_merged_output",
        merge_execution,
        [instructions_path, examples_path],
        output_path,
    )
