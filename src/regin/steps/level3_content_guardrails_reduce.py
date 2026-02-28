"""Level 3 — Reduce guardrail includes to inline string arrays.

Gate in: gate_paths_verified_input (reads verified TOML, returns JSON)
Gate out: gate_guardrails_reduced_output (validates JSON, writes TOML)
Include gates: gate_include_guardrails_constraints_input,
               gate_include_guardrails_anti_patterns_input
"""

from regin.functions.impure.gates import call_input_gate
from regin.functions.impure.runner import run_single
from regin.functions.pure.guardrails import reduce_guardrails
from regin.functions.pure.path_resolver import extract_str
from regin.structures.errors import GateValidationError
from regin.structures.paths_resolved import AgentPathsResolved


def load_include_content(model: AgentPathsResolved) -> dict[str, str]:
    """Load guardrail include files via include gates."""
    result: dict[str, str] = {}
    guardrails = model.criteria.guardrails
    pairs = [
        (guardrails.include_guardrails_constraints, "gate_include_guardrails_constraints_input"),
        (guardrails.include_guardrails_anti_patterns, "gate_include_guardrails_anti_patterns_input"),
    ]
    for include_ref, gate_name in pairs:
        if not include_ref:
            continue
        path = extract_str(include_ref.include)
        gate_result = call_input_gate(gate_name, path)
        if not gate_result.ok:
            err = gate_result.error
            raise GateValidationError(
                f"Include gate failed for {path}: {err.message if err else 'unknown'}",
            )
        result[path] = gate_result.data
    return result


def work(gated_json: str) -> str:
    """Transform delta: guardrail includes -> inline string arrays."""
    model = AgentPathsResolved.model_validate_json(gated_json)
    include_data = load_include_content(model)
    reduced = reduce_guardrails(model.criteria.guardrails, include_data)
    updated = model.criteria.model_copy(update={"guardrails": reduced})
    return model.model_copy(update={
        "criteria": updated,
    }).model_dump_json(by_alias=True, exclude_none=True)


def run(input_path: str, output_path: str) -> str:
    """Execute level 3: guardrails reduce. Returns output path."""
    return run_single(
        "gate_paths_verified_input",
        "gate_guardrails_reduced_output",
        work,
        input_path,
        output_path,
    )
