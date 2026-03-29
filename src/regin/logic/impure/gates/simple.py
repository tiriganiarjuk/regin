"""Gate validation — the IO boundary. CC=2-3 functions.

Validates gate results and formats errors. Gate modules are imported
directly by callers — this module provides the result validation only.
See gates/primitive.py for the NornirGate type alias and .validate() signatures.
"""

from pathlib import Path

from regin.logic.impure.gates.primitive import NornirGate
from regin.structure.model.gate_types import GateResult


def format_gate_error(gate_name: str, result: GateResult) -> str:
    """Build an error message from a failed gate result."""
    message = result.error.message if result.error else "Unknown gate error"
    error_type = result.error.type if result.error else "unknown"
    return f"Gate '{gate_name}' failed ({error_type}): {message}"


def validate_input(gate: NornirGate, file_path: Path) -> str:
    """Call an input gate. Returns validated JSON string."""
    gate_response = gate.validate(str(file_path))
    result = GateResult.model_validate(gate_response)
    if not result.ok:
        raise ValueError(format_gate_error(gate.__name__, result))
    return result.data


def validate_output(gate: NornirGate, json_data: str, file_path: Path) -> str:
    """Call an output gate. Validates JSON and writes TOML. Returns JSON."""
    gate_response = gate.validate(json_data, str(file_path))
    result = GateResult.model_validate(gate_response)
    if not result.ok:
        raise ValueError(format_gate_error(gate.__name__, result))
    return result.data


def validate_passthrough(gate: NornirGate, input_path: Path, output_path: Path) -> str:
    """Call a passthrough gate. Reads, validates, writes. Returns JSON."""
    gate_response = gate.validate(str(input_path), str(output_path))
    result = GateResult.model_validate(gate_response)
    if not result.ok:
        raise ValueError(format_gate_error(gate.__name__, result))
    return result.data
