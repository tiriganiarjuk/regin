"""Level 3 — Reduce instruction includes to inline steps.

Gate in: gate_paths_verified_input (reads verified TOML, returns JSON)
Gate out: gate_instructions_reduced_output (validates JSON, writes TOML)
Include gates: gate_include_execution_instructions_input (reads include files)
"""

from regin.functions.impure.gates import call_input_gate
from regin.functions.impure.runner import run_single
from regin.functions.pure.instructions import reduce_instructions
from regin.functions.pure.path_resolver import extract_str
from regin.structures.errors import GateValidationError
from regin.structures.paths_resolved import (
    AgentPathsResolved,
    ExecutionInstructions,
    IncludeInstruction,
)


def load_include_content(model: AgentPathsResolved) -> dict[str, str]:
    """Load instruction include files via include gates."""
    result: dict[str, str] = {}
    for item in model.execution.execution_instructions.root:
        if not isinstance(item, IncludeInstruction):
            continue
        path = extract_str(item.include)
        gate_result = call_input_gate(
            "gate_include_execution_instructions_input", path,
        )
        if not gate_result.ok:
            err = gate_result.error
            raise GateValidationError(
                f"Include gate failed for {path}: {err.message if err else 'unknown'}",
            )
        result[path] = gate_result.data
    return result


def work(gated_json: str) -> str:
    """Transform delta: instruction includes → inline steps."""
    model = AgentPathsResolved.model_validate_json(gated_json)
    include_data = load_include_content(model)
    reduced = reduce_instructions(model.execution.execution_instructions, include_data)
    updated = model.execution.model_copy(update={
        "execution_instructions": ExecutionInstructions(root=reduced),
    })
    return model.model_copy(update={
        "execution": updated,
    }).model_dump_json(by_alias=True, exclude_none=True)


def run(input_path: str, output_path: str) -> str:
    """Execute level 3: instructions reduce. Returns output path."""
    return run_single(
        "gate_paths_verified_input",
        "gate_instructions_reduced_output",
        work,
        input_path,
        output_path,
    )
