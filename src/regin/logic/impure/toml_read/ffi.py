"""FFI reader wrapper — Rust-side TOML read + schema validation.

CC=1. Thin wrapper around the PyO3 read_toml_validate_json module (nornir
readers/). Isolated in its own module so a missing compiled reader fails as
"import read_toml_validate_json" rather than inside a larger module.
"""

import read_toml_validate_json

from regin.structure.model.gate_types import GateRefusal, GateResult, GateSuccess


def read_toml(file_path: str, schema_name: str, schema_dir: str) -> GateSuccess | GateRefusal:
    """Read a TOML file, validate against the named schema, return the typed outcome.

    A GateSuccess carries the validated JSON string in `data`. A GateRefusal
    names the failure class in `error.type`.
    """
    result = read_toml_validate_json.read(file_path, schema_name, schema_dir)
    return GateResult.model_validate(result).root
