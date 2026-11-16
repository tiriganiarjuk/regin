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

from regin.logic.impure.registry.ffi import read_registry
from regin.logic.impure.registry.primitive import ai_home
from regin.structure.config.registry_location import RegistryLocation
from regin.structure.config.tool_registry import ToolRegistry, ToolRegistryEntry


def load_registry(location: RegistryLocation) -> list[ToolRegistryEntry]:
    """Load tool registry entries via the TOML reader. Raises ValueError when the reader reports failure."""
    registry_file = str(ai_home() / location.registry_path)
    result = read_registry(registry_file, location.schema_name, str(ai_home() / location.schema_dir))
    if not result.ok:
        raise ValueError(f"Tool registry read failed for {registry_file}: {result.error}")
    return ToolRegistry.model_validate_json(result.data).tools
