"""Collected grant path entries for hooks assembly.

Groups explicit and implicit tool/command entries that flow
from grant resolution into hooks config building.
"""

from pydantic import BaseModel, ConfigDict

from regin.structure.gen.schema.agent_anthropic_render import (
    CommandPathEntries,
    ToolPathEntries,
)


class GrantEntries(BaseModel):
    model_config = ConfigDict(frozen=True)

    explicit_tools: ToolPathEntries | None = None
    explicit_commands: CommandPathEntries | None = None
    implicit_tools: ToolPathEntries | None = None
    implicit_commands: CommandPathEntries | None = None
