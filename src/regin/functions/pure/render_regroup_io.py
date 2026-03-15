"""Regroup input and output data flow sections.

input: what the agent receives (format, delivery, schema, parameters, context).
output: what the agent produces (format, location, naming, schema).

Pure — receives typed model, returns typed model. No IO.
"""

from regin.structures.schema.agent_universal_format import AgentUniversalFormat
from regin.structures.schema import agent_universal_render as render


def regroup_input(source: AgentUniversalFormat) -> render.Input:
    """Assemble input from indirect.dispatch + security.schema + security.context."""
    dispatch = source.indirect.dispatch
    schema = source.security.security_schema
    context = source.security.context
    has_context = context and (context.context_required or context.context_available)
    return render.Input(
        description=render.InputDescription(dispatch.dispatch_input_description.root),
        format=render.DispatchInputFormat(dispatch.dispatch_input_format.value),
        delivery=render.DispatchInputDelivery(dispatch.dispatch_input_delivery.value),
        input_schema=render.PathExistsAbsolute(schema.input_schema.root) if schema.input_schema else None,
        parameters=render.DispatchParameters.model_validate_json(
            dispatch.dispatch_parameters.model_dump_json(by_alias=True)
        ) if dispatch.dispatch_parameters else None,
        context=render.ContextResources.model_validate_json(
            context.model_dump_json(by_alias=True)
        ) if has_context else None,
    )


def regroup_output(source: AgentUniversalFormat) -> render.Output:
    """Assemble output from task.processing + security.schema + security.io."""
    proc = source.task.processing
    schema = source.security.security_schema
    io_sec = source.security.security_io
    return render.Output(
        description=render.OutputDescription(proc.output_description.root),
        format=render.OutputFormatKind(proc.output_file_format.value),
        name_known=render.OutputNameKnown(proc.output_file_name_known.value),
        schema_path=render.PathExistsAbsolute(schema.output_schema.root) if schema.output_schema else None,
        schema_embed=render.Boolean(schema.output_schema_embed.root) if schema.output_schema_embed else None,
        output_file=render.PathAbsolute(io_sec.io_output_file.root) if io_sec.io_output_file else None,
        output_directory=render.PathAbsolute(io_sec.io_output_directory.root) if io_sec.io_output_directory else None,
        name_template=render.FilenameTemplate(proc.output_file_name_template.root) if proc.output_file_name_template else None,
        name_instruction=render.StringProse(proc.output_file_name_instruction.root) if proc.output_file_name_instruction else None,
    )
