"""Registry types for deployed Nornir writer tools.

Data loaded from tool_registry.toml by functions/impure/registry.py.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict


class OutputFormat(str, Enum):
    """Writer output format."""

    jsonl = "jsonl"
    json = "json"


class WriteFrequency(str, Enum):
    """How many records per invocation."""

    record = "record"
    batch = "batch"


class OutputPathKind(str, Enum):
    """Output path resolution strategy."""

    fixed_file = "fixed_file"
    directory_name = "directory_name"
    directory_prefix = "directory_prefix"


class ToolRegistryEntry(BaseModel):
    """A single deployed Nornir writer tool."""

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
