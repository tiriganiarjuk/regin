"""Gate loading and invocation — the IO boundary.

Loads compiled Nornir gate .so modules and calls their validate() methods.
This is the ONLY module that performs IO in regin. Every other module is pure.

Input gates: validate(file_path) -> {"ok", "data", "error"}
Output gates: validate(json_string, file_path) -> {"ok", "data", "error"}
Passthrough gate: validate(input_path, output_path) -> {"ok", "data", "error"}
"""

import functools
import importlib.util
from pathlib import Path
from types import ModuleType

from regin.structures.gate_types import GateResult

GATE_DIR = Path.home() / ".ai" / "tools" / "lib"


@functools.cache
def load_gate(name: str) -> ModuleType:
    """Load a compiled gate module by name, with caching."""
    so_name = f"{name}.cpython-313-darwin.so"
    so_path = GATE_DIR / so_name
    spec = importlib.util.spec_from_file_location(name, so_path)
    if spec is None or spec.loader is None:
        msg = f"Cannot load gate: {so_path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def format_gate_error(gate_name: str, result: GateResult) -> str:
    """Build an error message from a failed gate result."""
    message = result.error.message if result.error else "Unknown gate error"
    error_type = result.error.type if result.error else "unknown"
    return f"Gate '{gate_name}' failed ({error_type}): {message}"


def call_input_gate(gate_name: str, file_path: Path) -> str:
    """Call an input gate. Returns validated JSON string."""
    gate = load_gate(gate_name)
    raw = gate.validate(str(file_path))
    result = GateResult.model_validate(raw)
    if not result.ok:
        raise ValueError(format_gate_error(gate_name, result))
    return result.data


def call_output_gate(gate_name: str, json_data: str, file_path: Path) -> str:
    """Call an output gate. Validates JSON and writes TOML. Returns JSON."""
    gate = load_gate(gate_name)
    raw = gate.validate(json_data, str(file_path))
    result = GateResult.model_validate(raw)
    if not result.ok:
        raise ValueError(format_gate_error(gate_name, result))
    return result.data


def call_passthrough_gate(gate_name: str, input_path: Path, output_path: Path) -> str:
    """Call a passthrough gate. Reads, validates, writes. Returns JSON."""
    gate = load_gate(gate_name)
    raw = gate.validate(str(input_path), str(output_path))
    result = GateResult.model_validate(raw)
    if not result.ok:
        raise ValueError(format_gate_error(gate_name, result))
    return result.data
