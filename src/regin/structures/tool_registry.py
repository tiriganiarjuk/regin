"""Typed models for tool_registry.toml entries.

Hand-written — not generated from JSON Schema.
The tool registry is configuration, not a pipeline checkpoint.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict


class OutputFormat(Enum):
    json = "json"
    jsonl = "jsonl"


class WriteFrequency(Enum):
    record = "record"
    batch = "batch"


class OutputPathKind(Enum):
    fixed_file = "fixed_file"
    directory_name = "directory_name"
    directory_prefix = "directory_prefix"


class ToolRegistryEntry(BaseModel):
    model_config = ConfigDict(frozen=True)

    binary_name: str
    output_format: OutputFormat
    write_frequency: WriteFrequency
    output_path_kind: OutputPathKind
    schema_path: str
    file_path: str | None = None
    directory_path: str | None = None
    name_extension: str | None = None
    name_suffix: str | None = None
