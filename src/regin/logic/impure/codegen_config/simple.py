"""Codegen config loading — through the TOML reader into the typed model.

CC=1-2. Impure — the read happens in a compiled reader. Python never parses TOML.
"""

from pathlib import Path

from regin.logic.impure.toml_read.ffi import read_toml
from regin.structure.config.codegen_schemas import CodegenSchemasConfig


def load_codegen_schemas(config_path: Path, schema_dir: Path) -> CodegenSchemasConfig:
    """Load codegen_schemas.toml. Raises ValueError when the reader reports failure."""
    result = read_toml(str(config_path), "codegen-schemas", str(schema_dir))
    if not result.ok:
        raise ValueError(f"Codegen config read failed for {config_path}: {result.error}")
    return CodegenSchemasConfig.model_validate_json(result.data)
