"""Tool registry loader — the L8 registry read, through a reader gate.

CC=1-2. Impure — the read happens in a compiled reader (read_toml_validate_json),
which validates the TOML against nornir/schemas/tools/tool-registry.schema.json
and returns the gate contract: validated JSON on success, a typed error on
failure. Python never parses TOML.

Every reader failure is a hard failure here: L8 cannot resolve the output tool
without the registry.

The registry lives in the nornir project (not regin) because tool binaries are
deployment-specific, not definition-specific — the same agent definition should
resolve to different tool binaries depending on the deployment environment.
"""

from regin.logic.impure.gates.primitive import format_refusal
from regin.logic.impure.registry.primitive import ai_home
from regin.logic.impure.toml_read.ffi import read_toml
from regin.structure.config.registry_location import RegistryLocation
from regin.structure.config.tool_registry import ToolRegistry, ToolRegistryEntry
from regin.structure.model.gate_types import GateRefusal


def load_registry(location: RegistryLocation) -> list[ToolRegistryEntry]:
    """Load tool registry entries via the TOML reader. Raises ValueError when the reader reports failure."""
    registry_file = str(ai_home() / location.registry_path)
    outcome = read_toml(registry_file, location.schema_name, str(ai_home() / location.schema_dir))
    if isinstance(outcome, GateRefusal):
        refusal = format_refusal("read_toml_validate_json", outcome)
        raise ValueError(f"Tool registry read failed for {registry_file}: {refusal}")
    return ToolRegistry.model_validate_json(outcome.data).tools
