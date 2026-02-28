"""Uniform runner harness for all pipeline branches.

Every branch follows: gate_in(path) → work(json) → gate_out(json, path).
"""

from collections.abc import Callable
from loguru import logger

from regin.functions.impure.gates import (
    call_input_gate,
    call_output_gate,
    call_passthrough_gate,
)
from regin.structures.errors import GateValidationError


def check_gate_result(
    gate_name: str, ok: bool, error_type: str | None, error_msg: str | None,
) -> bool:
    """Raise GateValidationError if a gate failed. Returns True on success."""
    if not ok:
        raise GateValidationError(
            f"Gate {gate_name} failed ({error_type or 'unknown'}): {error_msg or 'no message'}",
        )
    return True


def run_single(
    gate_in_name: str,
    gate_out_name: str,
    work: Callable[[str], str],
    input_path: str,
    output_path: str,
) -> str:
    """Run a single-input branch: gate_in → work → gate_out. Returns output path."""
    logger.info("Running {} → {}", gate_in_name, gate_out_name)

    result_in = call_input_gate(gate_in_name, input_path)
    check_gate_result(
        gate_in_name, result_in.ok,
        result_in.error.type if result_in.error else None,
        result_in.error.message if result_in.error else None,
    )

    json_out = work(result_in.data)

    result_out = call_output_gate(gate_out_name, json_out, output_path)
    check_gate_result(
        gate_out_name, result_out.ok,
        result_out.error.type if result_out.error else None,
        result_out.error.message if result_out.error else None,
    )
    return output_path


def run_merge(
    gate_in_names: list[str],
    gate_out_name: str,
    work: Callable[..., str],
    input_paths: list[str],
    output_path: str,
) -> str:
    """Run a merge branch: multiple gate_ins → work → gate_out. Returns output path."""
    logger.info("Merging {} → {}", gate_in_names, gate_out_name)

    jsons: list[str] = []
    for gate_name, path in zip(gate_in_names, input_paths, strict=True):
        result = call_input_gate(gate_name, path)
        check_gate_result(
            gate_name, result.ok,
            result.error.type if result.error else None,
            result.error.message if result.error else None,
        )
        jsons.append(result.data)

    json_out = work(*jsons)

    result_out = call_output_gate(gate_out_name, json_out, output_path)
    check_gate_result(
        gate_out_name, result_out.ok,
        result_out.error.type if result_out.error else None,
        result_out.error.message if result_out.error else None,
    )
    return output_path


def run_passthrough(
    gate_name: str, input_path: str, output_path: str,
) -> str:
    """Run a passthrough gate: reads, validates, writes. No Python work. Returns output path."""
    logger.info("Passthrough {}", gate_name)

    result = call_passthrough_gate(gate_name, input_path, output_path)
    check_gate_result(
        gate_name, result.ok,
        result.error.type if result.error else None,
        result.error.message if result.error else None,
    )
    return output_path
