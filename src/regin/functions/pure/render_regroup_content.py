"""Regroup execution content and criteria sections.

instructions: ordered processing steps.
examples: example groups for the agent.
constraints: MUST/NEVER rules from guardrails.
anti_patterns: known failure patterns from guardrails.
return_format: how the agent reports results + success/failure criteria.

Pure — receives typed model, returns typed model. No IO.
"""

from regin.structures.schema.agent_universal_format import AgentUniversalFormat
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


def regroup_return_format(source: AgentUniversalFormat) -> render.ReturnFormat:
    """Assemble return format from task.return + security.schema + criteria."""
    ret = source.task.return_
    schema = source.security.security_schema
    return render.ReturnFormat(
        mode=render.ReturnMode(ret.return_mode.value),
        status_instruction=render.StringProse(ret.return_status.root) if ret.return_status else None,
        metrics_instruction=render.StringProse(ret.return_metrics.root) if ret.return_metrics else None,
        output_instruction=render.StringProse(ret.return_output.root) if ret.return_output else None,
        return_schema=render.PathExistsAbsolute(schema.return_schema.root) if schema.return_schema else None,
        success_criteria=render.SuccessCriteria.model_validate_json(
            source.criteria.success_criteria.model_dump_json(by_alias=True)
        ),
        failure_criteria=render.FailureCriteria.model_validate_json(
            source.criteria.failure_criteria.model_dump_json(by_alias=True)
        ),
    )
