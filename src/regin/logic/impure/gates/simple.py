"""Gate validation — the IO boundary. CC=1-2 functions.

Turns a gate's outcome into validated JSON or a completed write, or raises
with the refusal. Gate modules are imported directly by callers. The calls
themselves are in gates/primitive.py, with the NornirGate type alias and
the .validate() signatures.
"""

from pathlib import Path

from regin.logic.impure.gates.primitive import (
    NornirGate,
    call_defaults_gate,
    call_input_gate,
    call_output_gate,
    call_passthrough_gate,
    format_refusal,
)
from regin.structure.model.gate_types import GateRefusal, GateSuccess, GateWritten


def require_data(tool_name: str, outcome: GateSuccess | GateRefusal) -> str:
    """The validated JSON string of a success. A refusal raises."""
    if isinstance(outcome, GateRefusal):
        raise ValueError(format_refusal(tool_name, outcome))
    return outcome.data


def require_written(tool_name: str, outcome: GateWritten | GateRefusal) -> GateWritten:
    """The completed write of a success. A refusal raises."""
    if isinstance(outcome, GateRefusal):
        raise ValueError(format_refusal(tool_name, outcome))
    return outcome


def validate_input(gate: NornirGate, file_path: Path) -> str:
    """Call an input gate. Returns validated JSON string."""
    return require_data(gate.__name__, call_input_gate(gate, file_path))


def validate_defaults(gate: NornirGate, input_path: Path, output_path: Path) -> str:
    """Call a defaults gate. Reads, injects defaults, validates, writes. Returns the JSON it wrote."""
    return require_data(gate.__name__, call_defaults_gate(gate, input_path, output_path))


def validate_output(gate: NornirGate, json_data: str, file_path: Path) -> GateWritten:
    """Call an output gate. Validates JSON and writes TOML. Returns the completed write."""
    return require_written(gate.__name__, call_output_gate(gate, json_data, file_path))


def validate_passthrough(gate: NornirGate, input_path: Path, output_path: Path) -> GateWritten:
    """Call a passthrough gate. Reads, validates, writes. Returns the completed write."""
    return require_written(gate.__name__, call_passthrough_gate(gate, input_path, output_path))
