"""Level 5 — Merge execution-merged + criteria-merged into includes-merged.

Gate in: gate_execution_merged_input + gate_criteria_merged_input
Gate out: gate_includes_merged_output

Combines all resolved content into a single document (Red 4).
"""

from regin.functions.impure.runner import run_merge
from regin.functions.pure.mergers import merge_includes


def run(execution_path: str, criteria_path: str, output_path: str) -> str:
    """Execute level 5: includes merge. Returns output path."""
    return run_merge(
        ["gate_execution_merged_input", "gate_criteria_merged_input"],
        "gate_includes_merged_output",
        merge_includes,
        [execution_path, criteria_path],
        output_path,
    )
