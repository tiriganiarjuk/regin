"""Section regroup composed functions — multi-source section composition.

CC=4+. Import from simple and primitive within this module.
No cross-module composed imports.

Multi-branch assembly functions that reshape domain sections into consumption
sections. Each function here draws from multiple domain sections to compose
one consumption section. For example, regroup_identity combines
indirect.metadata, task.role, and task.processing — three separate authoring
concerns — into a single Identity section that the prompt renderer can emit
as a coherent block.

This is the core of the "regroup" concept: the 6-section domain model reflects
how the agent definition is authored (by concern area), while the 12-section
consumption model reflects how the rendered prompt is consumed (by the LLM
reading the prompt top-to-bottom).
"""

from regin.structure.gen.schema.agent_universal_format import AgentUniversalFormat
from regin.structure.gen.schema.agent_universal_render import (
    AgentCapabilityTier as RenderAgentCapabilityTier,
    AgentDescription as RenderAgentDescription,
    AgentName as RenderAgentName,
    Boolean as RenderBoolean,
    ContextAvailable as RenderContextAvailable,
    ContextRequired as RenderContextRequired,
    DispatchBackgroundMode as RenderDispatchBackgroundMode,
    DispatchBatchSize as RenderDispatchBatchSize,
    DispatchInputDelivery as RenderDispatchInputDelivery,
    DispatchInputFormat as RenderDispatchInputFormat,
    DispatchMode as RenderDispatchMode,
    DispatchParameters as RenderDispatchParameters,
    Dispatcher as RenderDispatcher,
    FilenameTemplate as RenderFilenameTemplate,
    Identity as RenderIdentity,
    Input as RenderInput,
    InputDescription as RenderInputDescription,
    Integer as RenderInteger,
    Output as RenderOutput,
    OutputDescription as RenderOutputDescription,
    OutputFormatKind as RenderOutputFormatKind,
    OutputNameKnown as RenderOutputNameKnown,
    PathAbsolute as RenderPathAbsolute,
    PathExistsAbsolute as RenderPathExistsAbsolute,
    ReturnFormat as RenderReturnFormat,
    ReturnMode as RenderReturnMode,
    RoleDescription as RenderRoleDescription,
    RoleExpertise as RenderRoleExpertise,
    RoleResponsibility as RenderRoleResponsibility,
    StringProse as RenderStringProse,
    StringText as RenderStringText,
    TitleString as RenderTitleString,
)

from regin.logic.transform.section_regroup.simple import guard_return_field


def regroup_identity(source: AgentUniversalFormat) -> RenderIdentity:
    """Assemble identity from indirect.metadata + task.role + task.processing.

    The title is derived from agent_name by capitalizing each hyphen-separated
    segment (e.g., "data-processor" -> "Data Processor"). The capability_tier
    flows through as-is and will be resolved to a concrete model name
    (haiku/sonnet/opus) in L8.
    """
    name = source.indirect.metadata.agent_name.root
    title = " ".join(word.capitalize() for word in name.split("-"))
    role = source.task.role
    return RenderIdentity(
        title=RenderTitleString(title),
        role_identity=RenderStringText(role.role_identity.root),
        role_responsibility=RenderRoleResponsibility(role.role_responsibility.root),
        capability_tier=RenderAgentCapabilityTier(source.task.processing.capability_model.value),
        role_description=RenderRoleDescription(role.role_description.root) if role.role_description else None,
        role_expertise=RenderRoleExpertise.model_validate_json(
            role.role_expertise.model_dump_json(by_alias=True)
        ) if role.role_expertise else None,
    )


def regroup_dispatcher(source: AgentUniversalFormat) -> RenderDispatcher:
    """Assemble dispatcher from indirect + task.processing + task.return.

    The dispatcher section is consumed by the orchestration system that launches
    this agent, not by the agent itself. It contains everything a dispatcher
    needs: how to invoke the agent (mode, background, input format/delivery),
    what resources it needs (parameters, batch size, max agents), and what to
    expect back (output format, return mode).
    """
    meta = source.indirect.metadata
    dispatch = source.indirect.dispatch
    processing = source.task.processing
    return_section = source.task.return_
    return RenderDispatcher(
        agent_name=RenderAgentName(meta.agent_name.root),
        agent_description=RenderAgentDescription(meta.agent_description.root),
        dispatch_mode=RenderDispatchMode(dispatch.dispatch_mode.value),
        background_mode=RenderDispatchBackgroundMode(dispatch.dispatch_background_mode.value),
        input_format=RenderDispatchInputFormat(dispatch.dispatch_input_format.value),
        input_delivery=RenderDispatchInputDelivery(dispatch.dispatch_input_delivery.value),
        input_description=RenderInputDescription(dispatch.dispatch_input_description.root),
        output_format=RenderOutputFormatKind(processing.output_file_format.value),
        output_name_known=RenderOutputNameKnown(processing.output_file_name_known.value),
        return_mode=RenderReturnMode(return_section.return_mode.value),
        max_agents=RenderInteger(dispatch.dispatch_max_agents.root) if dispatch.dispatch_max_agents else None,
        batch_size=RenderDispatchBatchSize.model_validate_json(
            dispatch.dispatch_batch_size.model_dump_json(by_alias=True)
        ) if dispatch.dispatch_batch_size else None,
        parameters=RenderDispatchParameters.model_validate_json(
            dispatch.dispatch_parameters.model_dump_json(by_alias=True)
        ) if dispatch.dispatch_parameters else None,
    )


def regroup_input(source: AgentUniversalFormat) -> RenderInput:
    """Assemble input from indirect.dispatch + security.schema + security.context.

    Combines three authoring concerns into one consumption block: the dispatch
    config (format, delivery, parameters), the validation schema (input_schema),
    and the context resources (required + available files the agent references).

    Authoring keeps the two context lists under one `context` group; the render
    schema carries them as siblings. The group has no rendering meaning — no
    heading, no control surface — so it is flattened here rather than passed on.
    """
    dispatch = source.indirect.dispatch
    schema = source.security.security_schema
    context = source.security.context
    required = context.context_required if context else None
    available = context.context_available if context else None
    return RenderInput(
        description=RenderInputDescription(dispatch.dispatch_input_description.root),
        format=RenderDispatchInputFormat(dispatch.dispatch_input_format.value),
        delivery=RenderDispatchInputDelivery(dispatch.dispatch_input_delivery.value),
        input_schema=RenderPathExistsAbsolute(schema.input_schema.root) if schema.input_schema else None,
        parameters=RenderDispatchParameters.model_validate_json(
            dispatch.dispatch_parameters.model_dump_json(by_alias=True)
        ) if dispatch.dispatch_parameters else None,
        context_required=RenderContextRequired.model_validate_json(
            required.model_dump_json(by_alias=True)
        ) if required else None,
        context_available=RenderContextAvailable.model_validate_json(
            available.model_dump_json(by_alias=True)
        ) if available else None,
    )


def regroup_output(source: AgentUniversalFormat) -> RenderOutput:
    """Assemble output from task.processing + security.schema + security.io.

    Combines processing config (format, naming convention, description),
    schema references (output_schema, embed flag), and IO paths (output_file,
    output_directory) into the output consumption section.
    """
    processing = source.task.processing
    schema = source.security.security_schema
    security_io = source.security.security_io
    return RenderOutput(
        description=RenderOutputDescription(processing.output_description.root),
        format=RenderOutputFormatKind(processing.output_file_format.value),
        name_known=RenderOutputNameKnown(processing.output_file_name_known.value),
        schema_path=RenderPathExistsAbsolute(schema.output_schema.root) if schema.output_schema else None,
        schema_embed=RenderBoolean(schema.output_schema_embed.root) if schema.output_schema_embed else None,
        output_file=RenderPathAbsolute(security_io.io_output_file.root) if security_io.io_output_file else None,
        output_directory=RenderPathAbsolute(security_io.io_output_directory.root) if security_io.io_output_directory else None,
        name_template=RenderFilenameTemplate(processing.output_file_name_template.root) if processing.output_file_name_template else None,
        name_instruction=RenderStringProse(processing.output_file_name_instruction.root) if processing.output_file_name_instruction else None,
    )


def regroup_return_format(source: AgentUniversalFormat) -> RenderReturnFormat:
    """Assemble return format from task.return + security.schema.

    Each return field is gated by the set of modes that include it:
    - "status" and "status-metrics" activate status_instruction
    - "status-metrics" and "metrics-output" activate metrics_instruction
    - "metrics-output" and "output" activate output_instruction

    This ensures the rendered prompt only asks for return components the
    dispatcher expects. Fields outside the active mode are forced to None.
    """
    return_section = source.task.return_
    mode = return_section.return_mode.value
    schema = source.security.security_schema
    status = guard_return_field(mode, {"status", "status-metrics"}, return_section.return_status)
    metrics = guard_return_field(mode, {"status-metrics", "metrics-output"}, return_section.return_metrics)
    output = guard_return_field(mode, {"metrics-output", "output"}, return_section.return_output)
    return RenderReturnFormat(
        mode=RenderReturnMode(mode),
        status_instruction=RenderStringProse(status.root) if status else None,
        metrics_instruction=RenderStringProse(metrics.root) if metrics else None,
        output_instruction=RenderStringProse(output.root) if output else None,
        return_schema=RenderPathExistsAbsolute(schema.return_schema.root) if schema.return_schema else None,
    )
