"""Vendor compose composed functions — vendor-specific section assembly.

CC=4+ functions. Import from simple and primitive within this module.
No cross-module composed imports — orchestration lives in orchestrate zone.

Complex section assembly for vendor-specific structures that have no universal
equivalent. Critical rules encode the most important behavioral constraints
(output tool usage) in a compact form for the prompt. Writing output carries
the resolved tool invocation details (tool name, variant, display text) that
the agent needs to produce correctly formatted output.
"""

from regin.structure.model.resolved_tool import ResolvedTool
from regin.structure.gen.schema.agent_universal_render import (
    EnforcementOutputTool as RenderEnforcementOutputTool,
    WritingOutput as RenderWritingOutput,
)
from regin.structure.gen.schema.agent_anthropic_render import (
    Boolean as AnthrBoolean,
    CriticalRules as AnthrCriticalRules,
    FilenameTemplate as AnthrFilenameTemplate,
    Integer as AnthrInteger,
    InvocationDisplay as AnthrInvocationDisplay,
    InvocationVariant as AnthrInvocationVariant,
    OutputToolBatchSize as AnthrOutputToolBatchSize,
    OutputToolNameNeeded as AnthrOutputToolNameNeeded,
    OutputToolSchemaXAbs as AnthrOutputToolSchemaXAbs,
    PathAbsolute as AnthrPathAbsolute,
    PathExistsAbsolute as AnthrPathExistsAbsolute,
    SnakeString as AnthrSnakeString,
    ToolName as AnthrToolName,
    WritingOutputAnthropic as AnthrWritingOutputAnthropic,
)


def compose_critical_rules(
    resolved_tool: ResolvedTool | None,
    writing_output: RenderWritingOutput | None,
    workspace_path: str,
) -> AnthrCriticalRules:
    """Compose critical rules — the highest-priority behavioral constraints.

    "Critical rules" are the subset of constraints that must appear prominently
    in the prompt. Currently: whether the agent has a custom output tool, and
    if so, its name, whether it needs to determine the filename, and the batch
    size. These are "critical" because violating them causes silent data loss
    or format corruption — unlike style constraints that degrade quality but
    don't break the pipeline.
    """
    has_tool = resolved_tool is not None
    tool_name = None
    name_needed = None
    batch_size = None

    if has_tool and writing_output is not None:
        output_tool = writing_output.writing_output
        tool_name = AnthrToolName(AnthrSnakeString(resolved_tool.tool_name))
        if output_tool.output_tool_name_needed is not None:
            name_needed = AnthrOutputToolNameNeeded(
                AnthrBoolean(output_tool.output_tool_name_needed.root)
            )
        if output_tool.output_tool_batch_size is not None:
            batch_size = AnthrOutputToolBatchSize(
                AnthrInteger(output_tool.output_tool_batch_size.root)
            )

    return AnthrCriticalRules(
        has_output_tool=AnthrBoolean(has_tool),
        tool_name=tool_name,
        name_needed=name_needed,
        batch_size=batch_size,
        workspace_path=AnthrPathExistsAbsolute(workspace_path) if workspace_path else None,
    )


def map_enforcement_fields(
    enforcement_tool: RenderEnforcementOutputTool,
) -> dict[str, AnthrFilenameTemplate | AnthrOutputToolBatchSize | AnthrOutputToolSchemaXAbs | AnthrPathAbsolute | None]:
    """Map enforcement output tool fields from universal to Anthropic types.

    Each field is independently nullable — the output tool spec is sparse by
    design, containing only the fields relevant to the agent's specific output
    configuration. A json-single-file agent has file_path but no directory_path;
    a jsonl-batch agent has directory_path and batch_size but no file_path.
    """
    return {
        "name_pattern": (
            AnthrFilenameTemplate(enforcement_tool.output_tool_name_pattern.root)
            if enforcement_tool.output_tool_name_pattern else None
        ),
        "batch_size": (
            AnthrOutputToolBatchSize(AnthrInteger(enforcement_tool.output_tool_batch_size.root))
            if enforcement_tool.output_tool_batch_size else None
        ),
        "schema_path": (
            AnthrOutputToolSchemaXAbs(enforcement_tool.output_tool_schema_path.root)
            if enforcement_tool.output_tool_schema_path else None
        ),
        "file_path": (
            AnthrPathAbsolute(enforcement_tool.output_tool_file_path.root)
            if enforcement_tool.output_tool_file_path else None
        ),
        "directory_path": (
            AnthrPathAbsolute(enforcement_tool.output_tool_directory_path.root)
            if enforcement_tool.output_tool_directory_path else None
        ),
    }


def compose_writing_output(
    resolved_tool: ResolvedTool | None,
    writing_output: RenderWritingOutput | None,
) -> AnthrWritingOutputAnthropic | None:
    """Populate vendor-specific writing output with resolved tool details.

    The invocation_variant ("with-name" or "no-name") determines which
    invocation pattern the rendered prompt will show the agent. The
    invocation_display is the human-readable example invocation.

    Returns None when no output tool was resolved (text/markdown agents
    or agents with no output path).
    """
    if resolved_tool is None or writing_output is None:
        return None
    output_tool = writing_output.writing_output
    name_needed = (
        output_tool.output_tool_name_needed is not None
        and output_tool.output_tool_name_needed.root is True
    )
    fields = map_enforcement_fields(output_tool)

    return AnthrWritingOutputAnthropic(
        tool_name=AnthrToolName(AnthrSnakeString(resolved_tool.tool_name)),
        invocation_variant=AnthrInvocationVariant(resolved_tool.invocation_variant),
        invocation_display=AnthrInvocationDisplay(resolved_tool.invocation_display),
        name_needed=AnthrOutputToolNameNeeded(AnthrBoolean(name_needed)),
        **fields,
    )


