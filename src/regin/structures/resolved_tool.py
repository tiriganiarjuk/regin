"""Resolved custom tool descriptor for step 2 of the anthropic resolver.

ResolvedTool: produced by successful custom tool discovery.
ToolBuildRequest: produced when no matching tool exists — contains
everything Nornir needs to build the missing writer.
"""

from pydantic import BaseModel, ConfigDict


class ResolvedTool(BaseModel):
    """Result of matching enforcement_output_tool spec to a workspace tool."""

    model_config = ConfigDict(frozen=True)

    tool_name: str
    invocation_variant: str  # "no-name" | "with-name"
    invocation_display: str  # ready bash heredoc


class ToolBuildRequest(BaseModel):
    """Nornir build specification for a missing custom output tool.

    Contains everything needed to create a new writer binary:
    the WriterConfig fields plus the agent that triggered the request.
    """

    model_config = ConfigDict(frozen=True)

    agent_name: str
    output_format: str
    write_frequency: str
    schema_path: str
    file_path: str | None = None
    directory_path: str | None = None
    name_needed: bool = False
    batch_size: int | None = None
