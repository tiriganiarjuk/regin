"""Blocking violation reported when a security definition fails Phase B checks.

Non-empty list of these blocks the DAG until the definition is fixed.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict


class BlockingCheck(Enum):
    output_path_in_allowed_write = "output_path_in_allowed_write"
    tempdir_collision = "tempdir_collision"
    scratch_overlaps_output = "scratch_overlaps_output"


class BlockingViolation(BaseModel):
    """A single blocking check failure with context for diagnostics."""

    model_config = ConfigDict(frozen=True)

    check: BlockingCheck
    message: str
    paths: tuple[str, ...]
