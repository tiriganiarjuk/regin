"""Hardcoded capability-to-path-type lookup table.

Used by path_operations to cross paths with effective capability sets.
"""

from regin.structure.gen.schema.agent_paths_resolved import Capabilities
from regin.structure.model.capability_tiers import CapabilityTiers

PATH_CAPABILITY_TIERS = CapabilityTiers(
    read=frozenset({Capabilities.read, Capabilities.search, Capabilities.inspect}),
    write=frozenset({
        Capabilities.read,
        Capabilities.search,
        Capabilities.inspect,
        Capabilities.write,
        Capabilities.edit,
        Capabilities.append,
    }),
)
