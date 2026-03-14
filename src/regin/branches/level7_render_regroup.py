"""Level 7 — Regroup domain sections into consumption sections.

Gate in:  gate_universal_format_input (reads TOML, returns validated JSON)
Gate out: gate_universal_render_output (validates JSON, writes TOML)
Delta:    6 domain sections (indirect, task, security, execution, criteria, enforcement)
          → 12 consumption sections (identity, security_boundary, implicit_grants,
          input, output, writing_output, constraints, anti_patterns, return_format,
          dispatcher, instructions, examples).
          One derived field: title from agent_name.
"""

from pathlib import Path

from regin.functions.impure.gates import call_input_gate, call_output_gate
from regin.functions.pure.render_regroup import regroup
from regin.structures.schema.agent_universal_format import AgentUniversalFormat


def run(input_path: Path, output_path: Path) -> str:
    """Execute the L7 render regroup branch. Returns output JSON."""
    json_in = call_input_gate("gate_universal_format_input", input_path)
    source = AgentUniversalFormat.model_validate_json(json_in)
    result = regroup(source)
    json_out = result.model_dump_json(by_alias=True, exclude_none=True)
    call_output_gate("gate_universal_render_output", json_out, output_path)
    return json_out
