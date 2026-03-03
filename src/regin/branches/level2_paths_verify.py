"""Level 2 — Verify all absolute paths exist on disk.

Gate: gate_paths_verified (passthrough — reads TOML, validates path existence, writes TOML)
Delta: NONE. The gate IS the branch. No Python transform.
"""

from pathlib import Path

from regin.functions.impure.gates import call_passthrough_gate


def run(input_path: Path, output_path: Path) -> str:
    """Execute the L2 paths verify branch. Returns validated JSON."""
    return call_passthrough_gate("gate_paths_verified", input_path, output_path)
