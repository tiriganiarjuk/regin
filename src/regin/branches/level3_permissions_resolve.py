"""Level 3 — Resolve security declarations into enforcement grants.

Gate in:  gate_paths_verified_input (reads TOML, returns validated JSON)
Gate out: gate_permissions_resolved_output (validates JSON, writes TOML)
Delta:    Input has security + processing declarations.
          Output adds enforcement section with explicit grants, implicit grants,
          and optional output tool.
"""

from pathlib import Path

from regin.functions.impure.gates import call_input_gate, call_output_gate
from regin.functions.pure.security_blocking import check_blocking
from regin.functions.pure.security_explicit import derive_explicit_grants
from regin.functions.pure.security_implicit import derive_implicit_grants
from regin.functions.pure.security_output_tool import assemble_output_tool
from regin.structures.schema.agent_paths_resolved import AgentPathsResolved
from regin.structures.schema.agent_permissions_resolved import (
    AgentPermissionsResolved,
    Criteria,
    Enforcement,
    Execution,
    Indirect,
    Security,
    Task,
)


def run(input_path: Path, output_path: Path) -> str:
    """Execute the L3 permissions resolve branch. Returns output JSON."""
    json_in = call_input_gate("gate_paths_verified_input", input_path)
    model = AgentPathsResolved.model_validate_json(json_in)
    violations = check_blocking(model.security)
    if violations:
        messages = [violation.message for violation in violations]
        raise ValueError(f"blocking check failed: {'; '.join(messages)}")
    enforcement = Enforcement(
        enforcement_explicit_grants=derive_explicit_grants(model.security),
        enforcement_implicit_grants=derive_implicit_grants(model.security),
        enforcement_output_tool=assemble_output_tool(model.security, model.task.processing),
    )
    resolved = AgentPermissionsResolved(
        indirect=Indirect.model_validate_json(model.indirect.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)),
        task=Task.model_validate_json(model.task.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)),
        security=Security.model_validate_json(model.security.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)),
        execution=Execution.model_validate_json(model.execution.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)),
        criteria=Criteria.model_validate_json(model.criteria.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)),
        enforcement=enforcement,
    )
    json_out = resolved.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    call_output_gate("gate_permissions_resolved_output", json_out, output_path)
    return json_out
