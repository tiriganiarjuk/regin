"""Level 3 — Resolve security permissions into enforcement grants.

Gate in: gate_paths_verified_input (reads verified TOML, returns JSON)
Gate out: gate_permissions_resolved_output (validates JSON, writes TOML)

Work function is pure: reads from security and task.processing sections.
"""

import json

from regin.functions.impure.runner import run_single
from regin.functions.pure.permissions import build_enforcement
from regin.structures.paths_resolved import AgentPathsResolved


def work(gated_json: str) -> str:
    """Transform delta: add enforcement section from security resolution."""
    model = AgentPathsResolved.model_validate_json(gated_json)
    enforcement = build_enforcement(
        model.security,
        model.task.processing,
        model.security.context,
    )
    base = json.loads(gated_json)
    base["enforcement"] = enforcement
    return json.dumps(base)


def run(input_path: str, output_path: str) -> str:
    """Execute level 3: permissions resolve. Returns output path."""
    return run_single(
        "gate_paths_verified_input",
        "gate_permissions_resolved_output",
        work,
        input_path,
        output_path,
    )
