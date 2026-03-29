"""Pre-resolved context for Anthropic render composition.

Groups all resolution outputs that flow from L8 orchestrate
into the vendor compose assembler.
"""

from pydantic import BaseModel, ConfigDict

from regin.structure.gen.schema.agent_anthropic_render import (
    AnthropicModel,
    DisplayEntries,
    HooksConfig,
    ToolPathEntries,
)
from regin.structure.model.resolved_tool import ResolvedTool


class AnthropicContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    model: AnthropicModel
    resolved_tool: ResolvedTool | None = None
    merged_tools: ToolPathEntries | None = None
    display: DisplayEntries | None = None
    hooks: HooksConfig
