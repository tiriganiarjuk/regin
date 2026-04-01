"""Verify all absolute paths exist on disk.

Gate: gate_paths_verified (passthrough — reads TOML, validates path existence, writes TOML)
Delta: NONE. The gate IS the branch. No Python transform.
"""

from pathlib import Path

import gate_paths_verified

from regin.logic.impure.gates.simple import validate_passthrough


def run(input_path: Path, output_path: Path) -> str:
    """Execute the paths verify branch. Returns validated JSON."""
    return validate_passthrough(gate_paths_verified, input_path, output_path)
