"""Orchestrate the domain-to-consumption regroup.

Calls 12 section assemblers from 4 domain modules to build the universal render.

Pure — receives typed model, returns typed model. No IO.
"""

from regin.structures.schema.agent_universal_format import AgentUniversalFormat
from regin.structures.schema import agent_universal_render as render

from regin.functions.pure.render_regroup_content import (
    regroup_anti_patterns,
    regroup_constraints,
    regroup_examples,
    regroup_instructions,
    regroup_return_format,
)
from regin.functions.pure.render_regroup_identity import (
    regroup_dispatcher,
    regroup_identity,
)
from regin.functions.pure.render_regroup_io import regroup_input, regroup_output
from regin.functions.pure.render_regroup_permissions import (
    regroup_implicit_grants,
    regroup_security_boundary,
    regroup_writing_output,
)


def regroup(source: AgentUniversalFormat) -> render.AgentUniversalRender:
    """Regroup 6 domain sections into 12 consumption sections."""
    return render.AgentUniversalRender(
        identity=regroup_identity(source),
        security_boundary=regroup_security_boundary(source),
        implicit_grants=regroup_implicit_grants(source),
        input=regroup_input(source),
        output=regroup_output(source),
        writing_output=regroup_writing_output(source),
        constraints=regroup_constraints(source),
        anti_patterns=regroup_anti_patterns(source),
        return_format=regroup_return_format(source),
        dispatcher=regroup_dispatcher(source),
        instructions=regroup_instructions(source),
        examples=regroup_examples(source),
    )
