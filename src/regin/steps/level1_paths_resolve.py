"""Level 1 — Resolve workspace-relative paths to absolute paths.

Gate in: gate_raw_definition_input (reads raw TOML, returns JSON)
Gate out: gate_paths_resolved_output (validates JSON, writes TOML)
"""

from regin.functions.impure.runner import run_single
from regin.functions.pure.path_resolver import resolve_all_paths
from regin.structures.raw_definition import AgentRawDefinition


def work(gated_json: str) -> str:
    """Transform delta: relative paths → absolute paths."""
    model = AgentRawDefinition.model_validate_json(gated_json)
    resolved = resolve_all_paths(model)
    return resolved.model_dump_json(by_alias=True, exclude_none=True)


def run(input_path: str, output_path: str) -> str:
    """Execute level 1: paths resolve. Returns output path."""
    return run_single(
        "gate_raw_definition_input",
        "gate_paths_resolved_output",
        work,
        input_path,
        output_path,
    )
