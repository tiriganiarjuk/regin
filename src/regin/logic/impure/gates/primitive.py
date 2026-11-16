"""Gate invocation primitive functions — call, type the outcome, return it.

CC=1. No error checking — caller decides what to do with the outcome.

NornirGate is a type alias for compiled Rust/PyO3 gate modules (.so files
at ~/ai/tools/lib/gate_*.cpython-313-darwin.so). Each gate module has a
.validate() method whose signature and success shape depend on the gate kind:

  Input gates:       gate.validate(file_path: str)                     data on success
  Defaults gates:    gate.validate(input_path: str, output_path: str)  data on success
  Output gates:      gate.validate(json_data: str, file_path: str)     no data on success
  Passthrough gates: gate.validate(input_path: str, output_path: str)  no data on success

All return {"ok": bool, "data": str | None, "error": {...} | None}.
Gate modules are imported by name (e.g. `import gate_raw_definition_input`).
"""

from pathlib import Path
from types import ModuleType

from regin.structure.model.gate_types import (
    GateRefusal,
    GateResult,
    GateSuccess,
    GateWriteResult,
    GateWritten,
)

type NornirGate = ModuleType


def format_refusal(tool_name: str, refusal: GateRefusal) -> str:
    """The message a refused call is raised with: tool, failure class, message."""
    return f"{tool_name} refused ({refusal.error.type}): {refusal.error.message}"


def call_input_gate(gate: NornirGate, file_path: Path) -> GateSuccess | GateRefusal:
    """Call an input gate, return its typed outcome."""
    return GateResult.model_validate(gate.validate(str(file_path))).root


def call_defaults_gate(
    gate: NornirGate, input_path: Path, output_path: Path,
) -> GateSuccess | GateRefusal:
    """Call a defaults gate, return its typed outcome."""
    return GateResult.model_validate(gate.validate(str(input_path), str(output_path))).root


def call_output_gate(
    gate: NornirGate, json_data: str, file_path: Path,
) -> GateWritten | GateRefusal:
    """Call an output gate, return its typed outcome."""
    return GateWriteResult.model_validate(gate.validate(json_data, str(file_path))).root


def call_passthrough_gate(
    gate: NornirGate, input_path: Path, output_path: Path,
) -> GateWritten | GateRefusal:
    """Call a passthrough gate, return its typed outcome."""
    return GateWriteResult.model_validate(gate.validate(str(input_path), str(output_path))).root
