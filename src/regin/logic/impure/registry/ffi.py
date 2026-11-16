"""FFI reader wrapper — Rust-side TOML read + schema validation.

CC=1. Thin wrapper around the PyO3 read_toml_validate_json module (nornir
readers/). Isolated in its own module so a missing compiled reader fails as
"import read_toml_validate_json" rather than inside a larger module.
"""

import read_toml_validate_json

from regin.structure.model.gate_types import GateResult


def read_registry(file_path: str, schema_name: str, schema_dir: str) -> GateResult:
    """Read the TOML registry, validate against the named schema, return the typed gate result.

    ok true: data is the validated JSON string. ok false: error names the failure class.
    """
    return GateResult.model_validate(read_toml_validate_json.read(file_path, schema_name, schema_dir))
