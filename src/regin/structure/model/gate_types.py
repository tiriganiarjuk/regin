"""Typed result of a Nornir gate or reader call.

Every call ends in one of two outcomes: a success, or a refusal carrying
its failure class and message. Each is its own model, so a result that is
neither fails validation where it arrives.

A success comes in two shapes, by what the tool is for. A tool that hands
data back (input gates, the defaults gate, readers) carries the validated
JSON string. A tool whose effect is the write (output gates, passthrough
gates) carries no data.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel


class GateError(BaseModel):
    """Why the call was refused: the failure class, and the message for people."""

    model_config = ConfigDict(frozen=True)

    type: str
    message: str


class GateSuccess(BaseModel):
    """The call succeeded and hands data back; `data` is the validated JSON."""

    model_config = ConfigDict(frozen=True)

    ok: Literal[True]
    data: str
    error: None


class GateWritten(BaseModel):
    """The call succeeded and its effect is the written file; there is no data."""

    model_config = ConfigDict(frozen=True)

    ok: Literal[True]
    data: None
    error: None


class GateRefusal(BaseModel):
    """The call was refused; `error` says in which class and why."""

    model_config = ConfigDict(frozen=True)

    ok: Literal[False]
    data: None
    error: GateError


class GateResult(RootModel[Annotated[GateSuccess | GateRefusal, Field(discriminator="ok")]]):
    """What an input gate, the defaults gate or a reader returns."""

    model_config = ConfigDict(frozen=True)


class GateWriteResult(RootModel[Annotated[GateWritten | GateRefusal, Field(discriminator="ok")]]):
    """What an output gate or a passthrough gate returns."""

    model_config = ConfigDict(frozen=True)
