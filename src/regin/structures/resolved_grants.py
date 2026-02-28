"""Intermediate types for the permissions resolution algorithm.

OutputMode classifies the enforcement output tool mode.

Grant accumulation uses dict[str, set[str]] directly — no wrapper class needed.
Capability keys: read, search, inspect, write, edit, append.
"""

from enum import Enum


class OutputMode(Enum):
    """Phase A classification of output enforcement mode."""

    enforced = "enforced"
    grant_only = "grant_only"
    none = "none"
