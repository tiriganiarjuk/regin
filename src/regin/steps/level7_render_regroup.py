"""Level 7 — Regroup universal format into consumption-oriented render sections.

Gate in: gate_universal_format_input (reads TOML, returns JSON)
Gate out: gate_universal_render_output (validates JSON, writes TOML)

Transforms 6 domain sections into 12 consumption sections (Red 7).
"""

from regin.functions.impure.runner import run_single
from regin.functions.pure.render import regroup


def run(input_path: str, output_path: str) -> str:
    """Execute level 7: render regroup. Returns output path."""
    return run_single(
        "gate_universal_format_input",
        "gate_universal_render_output",
        regroup,
        input_path,
        output_path,
    )
