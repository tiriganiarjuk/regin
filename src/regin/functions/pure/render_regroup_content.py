"""Regroup execution content and criteria sections.

instructions: ordered processing steps.
examples: example groups for the agent.
constraints: MUST/NEVER rules from guardrails.
anti_patterns: known failure patterns from guardrails.
return_format: how the agent reports results.
success_criteria: standalone success criteria section.
failure_criteria: standalone failure criteria section.

Pure — receives typed model, returns typed model. No IO.
"""

from regin.structures.schema.agent_universal_format import AgentUniversalFormat, StringProse
from regin.structures.schema import agent_universal_render as render


def regroup_instructions(source: AgentUniversalFormat) -> render.Instructions:
    """Wrap execution instructions for render consumption."""
    return render.Instructions(
        steps=render.ExecutionInstructions.model_validate_json(
            source.execution.execution_instructions.model_dump_json(by_alias=True)
        ),
    )


def regroup_examples(source: AgentUniversalFormat) -> render.Examples:
    """Wrap execution examples for render consumption."""
    return render.Examples(
        groups=render.ExecutionExamples.model_validate_json(
            source.execution.execution_examples.model_dump_json(by_alias=True)
        ),
    )


def regroup_constraints(source: AgentUniversalFormat) -> render.Constraints | None:
    """Wrap guardrail constraints. None when no constraints defined."""
    constraints = source.criteria.guardrails.guardrails_constraints
    if constraints is None:
        return None
    return render.Constraints(
        rules=render.GuardrailsConstraints.model_validate_json(
            constraints.model_dump_json(by_alias=True)
        ),
    )


def regroup_anti_patterns(source: AgentUniversalFormat) -> render.AntiPatterns | None:
    """Wrap guardrail anti-patterns. None when no anti-patterns defined."""
    anti_patterns = source.criteria.guardrails.guardrails_anti_patterns
    if anti_patterns is None:
        return None
    return render.AntiPatterns(
        patterns=render.GuardrailsAntiPatterns.model_validate_json(
            anti_patterns.model_dump_json(by_alias=True)
        ),
    )


def guard_return_field(
    mode: str, allowed_modes: set[str], field: StringProse | None,
) -> StringProse | None:
    """Return field value only when return_mode is in allowed set."""
    if mode not in allowed_modes or field is None:
        return None
    return field


def regroup_return_format(source: AgentUniversalFormat) -> render.ReturnFormat:
    """Assemble return format from task.return + security.schema + criteria."""
    ret = source.task.return_
    mode = ret.return_mode.value
    schema = source.security.security_schema
    status = guard_return_field(mode, {"status", "status-metrics"}, ret.return_status)
    metrics = guard_return_field(mode, {"status-metrics", "metrics-output"}, ret.return_metrics)
    output = guard_return_field(mode, {"metrics-output", "output"}, ret.return_output)
    return render.ReturnFormat(
        mode=render.ReturnMode(mode),
        status_instruction=render.StringProse(status.root) if status else None,
        metrics_instruction=render.StringProse(metrics.root) if metrics else None,
        output_instruction=render.StringProse(output.root) if output else None,
        return_schema=render.PathExistsAbsolute(schema.return_schema.root) if schema.return_schema else None,
    )


def regroup_success_criteria(source: AgentUniversalFormat) -> render.SuccessCriteria | None:
    """Wrap success criteria. None when no criteria defined."""
    criteria = source.criteria.success_criteria
    if criteria is None:
        return None
    return render.SuccessCriteria(
        criteria=render.SuccessCriteria1.model_validate_json(
            criteria.model_dump_json(by_alias=True)
        ),
    )


def regroup_failure_criteria(source: AgentUniversalFormat) -> render.FailureCriteria | None:
    """Wrap failure criteria. None when no criteria defined."""
    criteria = source.criteria.failure_criteria
    if criteria is None:
        return None
    return render.FailureCriteria(
        criteria=render.FailureCriteria1.model_validate_json(
            criteria.model_dump_json(by_alias=True)
        ),
    )
