"""Inject schema defaults into raw definition.

Gate: gate_raw_definition_defaults (defaults — reads TOML, injects defaults, writes TOML)
Delta: NONE. The gate IS the branch. No Python transform.
"""

from pathlib import Path

import gate_raw_definition_defaults

from regin.logic.impure.gates.simple import validate_defaults


def run(input_path: Path, output_path: Path) -> str:
    """Execute the defaults inject branch. Returns defaulted JSON."""
    return validate_defaults(gate_raw_definition_defaults, input_path, output_path)
