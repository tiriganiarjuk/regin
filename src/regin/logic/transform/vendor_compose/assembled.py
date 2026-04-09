"""Vendor compose assembled — top-level Anthropic composition entry point.

CC=1-2. Imports from composed and simple within this module.

Takes the universal render model and the pre-resolved AnthropicContext
(model, tool, display, hooks) and assembles all 14 Anthropic sections.

Most sections pass through unchanged (identical structure in both formats).
Three sections are vendor-specific: identity (adds resolved model),
security_boundary (adds display entries), and writing_output/critical_rules
(add resolved tool details). Frontmatter is entirely vendor-specific — it
has no universal equivalent.
"""

from regin.structure.gen.schema import agent_universal_render as render
from regin.structure.gen.schema import agent_anthropic_render as anthr
from regin.structure.model.anthropic_context import AnthropicContext

from regin.logic.transform.vendor_compose.primitive import compose_security_boundary
from regin.logic.transform.vendor_compose.simple import (
    compose_frontmatter,
    compose_identity,
    pass_through,
)
from regin.logic.transform.vendor_compose.composed import (
    compose_critical_rules,
    compose_writing_output,
)


def compose_anthropic_sections(
    source: render.AgentUniversalRender,
    context: AnthropicContext,
) -> anthr.AgentAnthropicRender:
    """Assemble all 14 Anthropic sections from universal render + context.

    The AnthropicContext carries everything resolved in L8 before this point:
    the concrete model name, the matched registry tool, the filesystem permissions,
    and the merged hooks config. This function wires those resolved values
    into the vendor-specific sections while passing through the rest unchanged.
    """
    identity = compose_identity(source.identity)
    workspace_path = source.security_boundary.workspace_path.root if source.security_boundary else ""

    return anthr.AgentAnthropicRender(
        identity=identity,
        security_boundary=compose_security_boundary(context.filesystem_permissions, workspace_path),
        input=pass_through(source.input, anthr.Input),
        output=pass_through(source.output, anthr.Output),
        writing_output=compose_writing_output(context.resolved_tool, source.writing_output),
        constraints=pass_through(source.constraints, anthr.Constraints),
        anti_patterns=pass_through(source.anti_patterns, anthr.AntiPatterns),
        success_criteria=pass_through(source.success_criteria, anthr.SuccessCriteria),
        failure_criteria=pass_through(source.failure_criteria, anthr.FailureCriteria),
        return_format=pass_through(source.return_format, anthr.ReturnFormat),
        dispatcher=pass_through(source.dispatcher, anthr.Dispatcher),
        instructions=pass_through(source.instructions, anthr.Instructions),
        examples=pass_through(source.examples, anthr.Examples),
        critical_rules=compose_critical_rules(context.resolved_tool, source.writing_output, workspace_path),
        frontmatter=compose_frontmatter(
            identity,
            anthr.AgentDescription(source.dispatcher.agent_description.root),
            context.model, context.hooks, context.merged_tools,
        ),
    )
