"""Level 1 — Resolve workspace-relative paths to absolute paths.

Gate in:  gate_raw_definition_input (reads raw definition TOML, returns JSON)
Gate out: gate_paths_resolved_output (validates JSON, writes paths-resolved TOML)
Delta:    Narrow path unions to absolute-only. Pydantic BeforeValidator on
          PathAbsolute/PathExistsAbsolute coerces relative paths during
          model construction. Gate enforces the type contract.
"""

from pathlib import Path

from regin.functions.impure.gates import call_input_gate, call_output_gate
from regin.structures.paths_resolved import AgentPathsResolved
from regin.structures.raw_definition import AgentRawDefinition


def run(input_path: Path, output_path: Path) -> str:
    """Execute the L1 paths resolve branch. Returns output JSON."""
    json_in = call_input_gate("gate_raw_definition_input", input_path)
    raw = AgentRawDefinition.model_validate_json(json_in)
    workspace = raw.security.security_paths.paths_workspace.root
    json_raw = raw.model_dump_json(by_alias=True, exclude_none=True)
    resolved = AgentPathsResolved.model_validate_json(
        json_raw, context={"workspace": workspace}
    )
    json_out = resolved.model_dump_json(by_alias=True, exclude_none=True)
    call_output_gate("gate_paths_resolved_output", json_out, output_path)
    return json_out
