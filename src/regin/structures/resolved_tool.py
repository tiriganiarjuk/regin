"""Intermediate type for custom tool discovery results.

Hand-written — not generated from JSON Schema.
Bridges the tool registry match to the anthropic render types.
"""

from pydantic import BaseModel, ConfigDict


class ResolvedTool(BaseModel):
    model_config = ConfigDict(frozen=True)

    tool_name: str
    invocation_variant: str  # "no-name" | "with-name"
    invocation_display: str  # composed bash heredoc
