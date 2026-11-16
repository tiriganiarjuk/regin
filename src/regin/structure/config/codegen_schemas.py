"""Codegen schemas config — which schemas become which generated modules.

The typed form of codegen_schemas.toml, validated against
schemas/config/codegen-schemas.schema.json by the TOML reader.
"""

from pydantic import BaseModel, ConfigDict


class CodegenSchemasConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    checkpoint: dict[str, str]
    include: dict[str, str]
