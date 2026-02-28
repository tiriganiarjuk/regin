"""Enums for the anthropic resolver (level 8).

Capability: the 6 abstract capabilities from the agent definition.
CapabilityTier: unresolved processing tiers from identity.
VendorTool: Claude Code tools that capabilities map to.
VendorCommand: shell commands that capabilities map to.
VendorModel: resolved Anthropic model names.
"""

from enum import Enum


class Capability(str, Enum):
    """Abstract capability keys from enforcement grants."""

    read = "read"
    search = "search"
    inspect = "inspect"
    write = "write"
    edit = "edit"
    append = "append"


class CapabilityTier(str, Enum):
    """Unresolved processing capability tiers."""

    fast_cheap = "fast-cheap"
    standard = "standard"
    analytical = "analytical"
    complex_reasoning = "complex-reasoning"
    max_capability = "max-capability"
    inherit = "inherit"


class VendorTool(str, Enum):
    """Claude Code tool names that capabilities explode into."""

    Read = "Read"
    Grep = "Grep"
    Glob = "Glob"
    Write = "Write"
    Edit = "Edit"


class VendorCommand(str, Enum):
    """Shell commands that capabilities explode into."""

    find = "find"
    ls = "ls"
    du = "du"
    wc = "wc"
    stat = "stat"
    diff = "diff"
    tree = "tree"


class VendorModel(str, Enum):
    """Resolved Anthropic model names."""

    haiku = "haiku"
    sonnet = "sonnet"
    opus = "opus"
    inherit = "inherit"
