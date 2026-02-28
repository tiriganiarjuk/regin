"""Level 8 — Resolve universal render into Anthropic platform render format.

Gate in: gate_universal_render_input (reads TOML, returns JSON)
Gate out: gate_anthropic_render_output (validates JSON, writes TOML)

Transforms 12 universal-render sections into 13 anthropic-render sections.
8 pass-through, 3 modified, 1 consumed, 2 created.
"""

from regin.functions.impure.registry import TOOL_REGISTRY
from regin.functions.impure.runner import run_single
from regin.functions.pure.anthropic_resolver import resolve


def run(input_path: str, output_path: str) -> str:
    """Execute level 8: anthropic resolve. Returns output path."""
    return run_single(
        "gate_universal_render_input",
        "gate_anthropic_render_output",
        lambda universal_json: resolve(universal_json, TOOL_REGISTRY),
        input_path,
        output_path,
    )
