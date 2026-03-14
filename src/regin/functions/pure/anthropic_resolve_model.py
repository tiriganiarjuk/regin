"""Step 1 — Resolve capability tier to Anthropic model name."""

from regin.structures.schema.agent_anthropic_render import AnthropicModel
from regin.structures.schema.agent_universal_render import AgentCapabilityTier


def resolve_model(tier: AgentCapabilityTier) -> AnthropicModel:
    """Map capability tier to Anthropic model name."""
    match tier:
        case AgentCapabilityTier.fast_cheap:
            return AnthropicModel.haiku
        case AgentCapabilityTier.standard | AgentCapabilityTier.analytical:
            return AnthropicModel.sonnet
        case AgentCapabilityTier.complex_reasoning | AgentCapabilityTier.max_capability:
            return AnthropicModel.opus
        case AgentCapabilityTier.inherit:
            return AnthropicModel.inherit
