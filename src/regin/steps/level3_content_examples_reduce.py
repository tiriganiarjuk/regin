"""Level 3 — Reduce example includes to inline groups and entries.

Gate in: gate_paths_verified_input (reads verified TOML, returns JSON)
Gate out: gate_examples_reduced_output (validates JSON, writes TOML)
Include gates: gate_include_example_group_input, gate_include_example_entries_input
"""

from regin.functions.impure.gates import call_input_gate
from regin.functions.impure.runner import run_single
from regin.functions.pure.examples import reduce_examples
from regin.functions.pure.path_resolver import extract_str
from regin.structures.errors import GateValidationError
from regin.structures.paths_resolved import (
    AgentPathsResolved,
    ExampleGroup,
    ExecutionExamples,
    IncludeExample,
    IncludeExampleGroup,
)


def load_include_content(model: AgentPathsResolved) -> dict[str, str]:
    """Load all example include files via include gates."""
    result: dict[str, str] = {}
    for item in model.execution.execution_examples.root:
        if isinstance(item, IncludeExampleGroup):
            path = extract_str(item.include)
            gate_name = "gate_include_example_group_input"
        elif isinstance(item, ExampleGroup) and item.example_entries:
            for entry in item.example_entries.root:
                if not isinstance(entry, IncludeExample):
                    continue
                path = extract_str(entry.include)
                gate_result = call_input_gate(
                    "gate_include_example_entries_input", path,
                )
                if not gate_result.ok:
                    err = gate_result.error
                    raise GateValidationError(
                        f"Include gate failed for {path}: {err.message if err else 'unknown'}",
                    )
                result[path] = gate_result.data
            continue
        else:
            continue
        gate_result = call_input_gate(gate_name, path)
        if not gate_result.ok:
            err = gate_result.error
            raise GateValidationError(
                f"Include gate failed for {path}: {err.message if err else 'unknown'}",
            )
        result[path] = gate_result.data
    return result


def work(gated_json: str) -> str:
    """Transform delta: example includes -> inline groups and entries."""
    model = AgentPathsResolved.model_validate_json(gated_json)
    include_data = load_include_content(model)
    reduced = reduce_examples(model.execution.execution_examples, include_data)
    updated = model.execution.model_copy(update={
        "execution_examples": ExecutionExamples(root=reduced),
    })
    return model.model_copy(update={
        "execution": updated,
    }).model_dump_json(by_alias=True, exclude_none=True)


def run(input_path: str, output_path: str) -> str:
    """Execute level 3: examples reduce. Returns output path."""
    return run_single(
        "gate_paths_verified_input",
        "gate_examples_reduced_output",
        work,
        input_path,
        output_path,
    )
