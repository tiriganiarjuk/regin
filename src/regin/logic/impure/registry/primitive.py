"""Registry primitives — workspace root resolution.

CC=1. Impure: touches the environment (home directory).
"""

from pathlib import Path


def ai_home() -> Path:
    """The ai workspace root: $HOME/ai."""
    return Path.home() / "ai"
