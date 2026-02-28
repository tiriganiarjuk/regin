"""Level 6 — Converge content + permissions branches into universal format.

Gate in: gate_includes_merged_input + gate_permissions_resolved_input
Gate out: gate_universal_format_output

Takes content (execution + criteria) from includes-merged,
enforcement from permissions-resolved. Output is Red 6.
"""

from regin.functions.impure.runner import run_merge
from regin.functions.pure.mergers import merge_universal


def run(content_path: str, permissions_path: str, output_path: str) -> str:
    """Execute level 6: universal merge. Returns output path."""
    return run_merge(
        ["gate_includes_merged_input", "gate_permissions_resolved_input"],
        "gate_universal_format_output",
        merge_universal,
        [content_path, permissions_path],
        output_path,
    )
