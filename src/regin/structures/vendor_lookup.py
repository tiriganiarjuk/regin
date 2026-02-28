"""Vendor lookup tables for the anthropic resolver.

Three frozen lookup tables mapping abstract capabilities and tiers
to vendor-specific tools, commands, and models. Singleton: ANTHROPIC.
"""

from pydantic import BaseModel, ConfigDict

from regin.structures.enums import (
    Capability,
    CapabilityTier,
    VendorCommand,
    VendorModel,
    VendorTool,
)


class VendorLookup(BaseModel):
    """Frozen lookup tables for one vendor platform."""

    model_config = ConfigDict(frozen=True)

    capability_to_tools: dict[Capability, tuple[VendorTool, ...]]
    capability_to_commands: dict[Capability, tuple[VendorCommand, ...]]
    tier_to_model: dict[CapabilityTier, VendorModel]


ANTHROPIC = VendorLookup(
    capability_to_tools={
        Capability.read: (VendorTool.Read,),
        Capability.search: (VendorTool.Grep, VendorTool.Glob),
        Capability.inspect: (VendorTool.Read,),
        Capability.write: (VendorTool.Write,),
        Capability.edit: (VendorTool.Edit,),
        Capability.append: (VendorTool.Edit,),
    },
    capability_to_commands={
        Capability.search: (VendorCommand.find,),
        Capability.inspect: (
            VendorCommand.ls,
            VendorCommand.du,
            VendorCommand.wc,
            VendorCommand.stat,
            VendorCommand.diff,
            VendorCommand.tree,
        ),
    },
    tier_to_model={
        CapabilityTier.fast_cheap: VendorModel.haiku,
        CapabilityTier.standard: VendorModel.sonnet,
        CapabilityTier.analytical: VendorModel.sonnet,
        CapabilityTier.complex_reasoning: VendorModel.opus,
        CapabilityTier.max_capability: VendorModel.opus,
        CapabilityTier.inherit: VendorModel.inherit,
    },
)
