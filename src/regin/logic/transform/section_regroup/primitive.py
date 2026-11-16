"""Section regroup primitive functions — direct pass-through wraps.

CC=1. No branching. No cross-module dependencies.

Direct wrappers that copy execution content (instructions, examples) from
the domain format (AgentUniversalFormat) into the consumption format
(AgentUniversalRender). These sections pass through without restructuring
because their consumption shape already matches their authoring shape —
instruction steps and example groups are already consumption-oriented.

The JSON round-trip (dump -> validate) ensures Pydantic alias rules and
schema validation are applied during the type crossing.
"""

from regin.structure.gen.schema.agent_universal_format import AgentUniversalFormat
from regin.structure.gen.schema.agent_universal_render import (
    Examples as RenderExamples,
    ExecutionExamples as RenderExecutionExamples,
    ExecutionInstructions as RenderExecutionInstructions,
    Instructions as RenderInstructions,
)


def regroup_instructions(source: AgentUniversalFormat) -> RenderInstructions:
    """Copy execution instructions into the render consumption model.

    Instructions are authored as a flat list of steps in the execution section
    and consumed as the same flat list — no structural change needed.
    """
    return RenderInstructions(
        steps=RenderExecutionInstructions.model_validate_json(
            source.execution.execution_instructions.model_dump_json(by_alias=True)
        ),
    )


def regroup_examples(source: AgentUniversalFormat) -> RenderExamples:
    """Copy execution examples into the render consumption model.

    Example groups are authored as nested structures (group -> entries) and
    consumed in the same shape — no structural change needed.
    """
    return RenderExamples(
        groups=RenderExecutionExamples.model_validate_json(
            source.execution.execution_examples.model_dump_json(by_alias=True)
        ),
    )
