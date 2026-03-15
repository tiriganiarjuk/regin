"""Level 0 — Inject schema defaults into raw definition.

Gate: gate_raw_definition_defaults (passthrough — reads TOML, injects defaults, writes TOML)
Delta: NONE. The gate IS the branch. No Python transform.
"""

from pathlib import Path

from regin.functions.impure.gates import call_passthrough_gate


def run(input_path: Path, output_path: Path) -> str:
    """Execute the L0 defaults inject branch. Returns defaulted JSON."""
    return call_passthrough_gate("gate_raw_definition_defaults", input_path, output_path)
