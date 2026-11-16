"""Section regroup assembled — top-level domain-to-consumption transform.

CC=1-2. Imports from composed, simple, and primitive within this module.

Transforms the 6-section domain model (indirect, task, security, execution,
criteria, enforcement) into the 12-section consumption model (identity,
security_boundary, implicit_grants, input, output, writing_output,
constraints, anti_patterns, return_format, success_criteria, failure_criteria,
dispatcher, instructions, examples).

The constraints, anti_patterns, success_criteria, and failure_criteria sections
use the generic wrap_nullable path because they are simple 1:1 copies with
Optional handling. The remaining sections have dedicated regroup functions
because they draw from multiple domain sections.
"""

from regin.structure.gen.schema.agent_universal_format import AgentUniversalFormat
from regin.structure.gen.schema.agent_universal_render import (
    AgentUniversalRender as RenderAgentUniversalRender,
    AntiPatterns as RenderAntiPatterns,
    Constraints as RenderConstraints,
    FailureCriteria as RenderFailureCriteria,
    FailureCriteria1 as RenderFailureCriteria1,
    GuardrailsAntiPatterns as RenderGuardrailsAntiPatterns,
    GuardrailsConstraints as RenderGuardrailsConstraints,
    SuccessCriteria as RenderSuccessCriteria,
    SuccessCriteria1 as RenderSuccessCriteria1,
)

from regin.logic.transform.section_regroup.primitive import (
    regroup_examples,
    regroup_instructions,
)
from regin.logic.transform.section_regroup.simple import (
    regroup_implicit_grants,
    regroup_security_boundary,
    regroup_writing_output,
    wrap_nullable,
)
from regin.logic.transform.section_regroup.composed import (
    regroup_dispatcher,
    regroup_identity,
    regroup_input,
    regroup_output,
    regroup_return_format,
)


def regroup(source: AgentUniversalFormat) -> RenderAgentUniversalRender:
    """Regroup 6 domain sections into 12 consumption sections.

    Each call delegates to a level-appropriate function: primitive for direct
    pass-through, simple for null-safe wrapping, composed for multi-source
    assembly. The result is the universal render model ready for L8 vendor
    composition.
    """
    return RenderAgentUniversalRender(
        identity=regroup_identity(source),
        security_boundary=regroup_security_boundary(source),
        implicit_grants=regroup_implicit_grants(source),
        input=regroup_input(source),
        output=regroup_output(source),
        writing_output=regroup_writing_output(source),
        constraints=wrap_nullable(
            source.criteria.guardrails.guardrails_constraints,
            RenderConstraints, "rules", RenderGuardrailsConstraints,
        ),
        anti_patterns=wrap_nullable(
            source.criteria.guardrails.guardrails_anti_patterns,
            RenderAntiPatterns, "patterns", RenderGuardrailsAntiPatterns,
        ),
        return_format=regroup_return_format(source),
        success_criteria=wrap_nullable(
            source.criteria.success_criteria,
            RenderSuccessCriteria, "criteria", RenderSuccessCriteria1,
        ),
        failure_criteria=wrap_nullable(
            source.criteria.failure_criteria,
            RenderFailureCriteria, "criteria", RenderFailureCriteria1,
        ),
        dispatcher=regroup_dispatcher(source),
        instructions=regroup_instructions(source),
        examples=regroup_examples(source),
    )
