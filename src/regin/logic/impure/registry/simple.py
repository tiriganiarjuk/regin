"""Tool registry loader — the L8 registry read, through a reader gate.

CC=1-2. Impure — the read happens in a compiled reader (read_toml_validate_json),
which validates the TOML against nornir/schemas/tools/tool-registry.schema.json
and returns a JSON string. Python never parses TOML.

The registry lives in the nornir project (not regin) because tool binaries are
deployment-specific, not definition-specific — the same agent definition should
resolve to different tool binaries depending on the deployment environment.
"""

from regin.logic.impure.registry.ffi import read_registry
from regin.logic.impure.registry.primitive import ai_home
from regin.structure.config.registry_location import RegistryLocation
from regin.structure.config.tool_registry import ToolRegistry, ToolRegistryEntry


def load_registry(location: RegistryLocation) -> list[ToolRegistryEntry]:
    """Load tool registry entries via the TOML reader. Raises ValueError on validation failure."""
    base = ai_home()
    json_text = read_registry(
        str(base / location.registry_path),
        location.schema_name,
        str(base / location.schema_dir),
    )
    return ToolRegistry.model_validate_json(json_text).tools
