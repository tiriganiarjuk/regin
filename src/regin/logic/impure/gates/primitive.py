"""Gate invocation primitive functions — call and return.

CC=1. No error checking — caller decides what to do with the result.

NornirGate is a type alias for compiled Rust/PyO3 gate modules (.so files
at ~/ai/tools/lib/gate_*.cpython-313-darwin.so). Each gate module has a
.validate() method whose signature depends on the gate kind:

  Input gates:       gate.validate(file_path: str) -> dict
  Output gates:      gate.validate(json_data: str, file_path: str) -> dict
  Passthrough gates: gate.validate(input_path: str, output_path: str) -> dict

All return {"ok": bool, "data": str | None, "error": {...} | None}.
Gate modules are imported by name (e.g. `import gate_raw_definition_input`).
"""

from pathlib import Path
from types import ModuleType

from regin.structure.model.gate_types import GateResult

type NornirGate = ModuleType


def call_input_gate(gate: NornirGate, file_path: Path) -> GateResult:
    """Call an input gate, return the raw validated result."""
    return GateResult.model_validate(gate.validate(str(file_path)))


def call_output_gate(gate: NornirGate, json_data: str, file_path: Path) -> GateResult:
    """Call an output gate, return the raw validated result."""
    return GateResult.model_validate(gate.validate(json_data, str(file_path)))


def call_passthrough_gate(gate: NornirGate, input_path: Path, output_path: Path) -> GateResult:
    """Call a passthrough gate, return the raw validated result."""
    return GateResult.model_validate(gate.validate(str(input_path), str(output_path)))
