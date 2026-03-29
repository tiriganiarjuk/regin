"""Capability-to-path-type model for permission intersection.

Defines which capabilities are available via read paths vs write paths.
"""

from pydantic import BaseModel, ConfigDict

from regin.structure.gen.schema.agent_paths_resolved import Capabilities


class CapabilityTiers(BaseModel):
    """Frozen mapping of capabilities reachable via each path type."""

    model_config = ConfigDict(frozen=True)

    read: frozenset[Capabilities]
    write: frozenset[Capabilities]
