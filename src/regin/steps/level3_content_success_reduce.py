"""Level 3 — Reduce success/failure criteria includes to inline items.

Gate in: gate_paths_verified_input (reads verified TOML, returns JSON)
Gate out: gate_success_reduced_output (validates JSON, writes TOML)
Include gates: gate_include_success_criteria_input,
               gate_include_failure_criteria_input
"""

from regin.functions.impure.gates import call_input_gate
from regin.functions.impure.runner import run_single
from regin.functions.pure.path_resolver import extract_str
from regin.functions.pure.success_criteria import (
    reduce_failure_criteria,
    reduce_success_criteria,
)
from regin.structures.errors import GateValidationError
from regin.structures.paths_resolved import (
    AgentPathsResolved,
    FailureCriteria,
    IncludeFailureCriteria,
    IncludeSuccessCriteria,
    SuccessCriteria,
)


def load_include_content(model: AgentPathsResolved) -> dict[str, str]:
    """Load criteria include files via include gates."""
    result: dict[str, str] = {}
    criteria = model.criteria
    gate_map = [
        (criteria.success_criteria.root, IncludeSuccessCriteria, "gate_include_success_criteria_input"),
        (criteria.failure_criteria.root, IncludeFailureCriteria, "gate_include_failure_criteria_input"),
    ]
    for items, include_type, gate_name in gate_map:
        for item in items:
            if not isinstance(item, include_type):
                continue
            path = extract_str(item.include)
            gate_result = call_input_gate(gate_name, path)
            if not gate_result.ok:
                err = gate_result.error
                raise GateValidationError(
                    f"Include gate failed for {path}: {err.message if err else 'unknown'}",
                )
            result[path] = gate_result.data
    return result


def work(gated_json: str) -> str:
    """Transform delta: criteria includes -> inline items."""
    model = AgentPathsResolved.model_validate_json(gated_json)
    criteria = model.criteria
    include_data = load_include_content(model)
    success = reduce_success_criteria(criteria.success_criteria, include_data)
    failure = reduce_failure_criteria(criteria.failure_criteria, include_data)
    updated = criteria.model_copy(update={
        "success_criteria": SuccessCriteria(root=success),
        "failure_criteria": FailureCriteria(root=failure),
    })
    return model.model_copy(update={
        "criteria": updated,
    }).model_dump_json(by_alias=True, exclude_none=True)


def run(input_path: str, output_path: str) -> str:
    """Execute level 3: success/failure criteria reduce. Returns output path."""
    return run_single(
        "gate_paths_verified_input",
        "gate_success_reduced_output",
        work,
        input_path,
        output_path,
    )
