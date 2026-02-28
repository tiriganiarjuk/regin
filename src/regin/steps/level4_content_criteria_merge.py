"""Level 4 — Merge guardrails-reduced + success-reduced.

Gate in: gate_guardrails_reduced_input + gate_success_reduced_input
Gate out: gate_criteria_merged_output

Takes inlined guardrails from one branch, inlined success/failure from the other.
"""

from regin.functions.impure.runner import run_merge
from regin.functions.pure.mergers import merge_criteria


def run(guardrails_path: str, success_path: str, output_path: str) -> str:
    """Execute level 4: criteria merge. Returns output path."""
    return run_merge(
        ["gate_guardrails_reduced_input", "gate_success_reduced_input"],
        "gate_criteria_merged_output",
        merge_criteria,
        [guardrails_path, success_path],
        output_path,
    )
