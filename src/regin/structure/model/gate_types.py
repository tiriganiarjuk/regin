"""Typed wrappers for Nornir gate return values.

Gates return {"ok": bool, "data": str | None, "error": {"type": str, "message": str} | None}.
These models make that shape explicit and frozen.
"""

from pydantic import BaseModel, ConfigDict


class GateError(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: str
    message: str


class GateResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    ok: bool
    data: str | None = None
    error: GateError | None = None
