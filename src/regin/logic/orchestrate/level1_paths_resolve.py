"""Level 1 — Resolve workspace-relative paths to absolute paths.

Gate in:  gate_raw_definition_input (reads raw definition TOML, returns JSON)
Gate out: gate_paths_resolved_output (validates JSON, writes paths-resolved TOML)
Delta:    Narrow path unions to absolute-only. Explicit transform walks the
          model tree and resolves relative paths before re-validation.
          Gate enforces the type contract.
"""

from pathlib import Path

import gate_paths_resolved_output
import gate_raw_definition_input

from regin.logic.impure.gates.simple import validate_input, validate_output
from regin.logic.transform.paths_resolve.composed import resolve_paths_in_model
from regin.structure.gen.schema.agent_paths_resolved import AgentPathsResolved
from regin.structure.gen.schema.agent_raw_definition import AgentRawDefinition


def run(input_path: Path, output_path: Path) -> str:
    """Execute the L1 paths resolve branch. Returns output JSON."""
    json_in = validate_input(gate_raw_definition_input, input_path)
    raw_definition = AgentRawDefinition.model_validate_json(json_in)
    workspace = raw_definition.security.security_paths.paths_workspace.root
    json_resolved = resolve_paths_in_model(raw_definition, workspace)
    resolved = AgentPathsResolved.model_validate_json(json_resolved)
    json_out = resolved.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    validate_output(gate_paths_resolved_output, json_out, output_path)
    return json_out
