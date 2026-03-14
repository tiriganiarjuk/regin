"""Level 8 — Resolve universal render into Anthropic platform format.

Gate in:  gate_universal_render_input (reads TOML, returns validated JSON)
Gate out: gate_anthropic_render_output (validates JSON, writes TOML)
Delta:    12 consumption sections → 13 Anthropic sections.
          8 pass-through, 3 modified, 1 consumed, 2 created.
          Model resolved, grants exploded, hooks built, frontmatter composed.
"""

from pathlib import Path

from regin.functions.impure.gates import call_input_gate, call_output_gate
from regin.functions.impure.registry import load_registry
from regin.functions.pure.anthropic_resolve_sections import resolve_anthropic
from regin.structures.schema.agent_universal_render import AgentUniversalRender


def run(input_path: Path, output_path: Path) -> str:
    """Execute the L8 anthropic resolve branch. Returns output JSON."""
    json_in = call_input_gate("gate_universal_render_input", input_path)
    source = AgentUniversalRender.model_validate_json(json_in)
    registry = load_registry()
    result = resolve_anthropic(source, registry)
    json_out = result.model_dump_json(by_alias=True, exclude_none=True)
    call_output_gate("gate_anthropic_render_output", json_out, output_path)
    return json_out
