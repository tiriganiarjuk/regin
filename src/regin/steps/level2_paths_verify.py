"""Level 2 — Verify all absolute paths exist on disk.

Gate: gate_paths_verified (passthrough — reads, validates paths, writes)
No Python transform. The gate handles everything.
"""

from regin.functions.impure.runner import run_passthrough


def run(input_path: str, output_path: str) -> str:
    """Execute level 2: paths verify (passthrough). Returns output path."""
    return run_passthrough("gate_paths_verified", input_path, output_path)
