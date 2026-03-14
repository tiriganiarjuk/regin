"""Assemble enforcement output tool from security and processing fields.

Collects output-related declarations into the tool section.
No tool-vs-grant decision — downstream resolves that.

Pure — reads typed models, returns typed model.
"""

from regin.structures.schema.agent_paths_resolved import (
    OutputFileNameKnown,
    Processing,
    Security,
)
from regin.structures.schema.agent_permissions_resolved import (
    Boolean,
    EnforcementOutputTool,
    Integer,
    OutputFormatKind,
    WriteFrequency,
)


def assemble_output_tool(
    security: Security,
    processing: Processing,
) -> EnforcementOutputTool | None:
    """Collect output fields into enforcement tool spec. None if no output path."""
    io_section = security.security_io
    output_file = io_section.io_output_file
    output_directory = io_section.io_output_directory
    if not output_file and not output_directory:
        return None
    tool_format = OutputFormatKind(processing.output_file_format.value)
    if tool_format in (OutputFormatKind.text, OutputFormatKind.markdown):
        return None
    schema_path = security.security_schema.output_schema
    write_freq = processing.output_write_frequency
    name_known = processing.output_file_name_known
    return EnforcementOutputTool(
        output_tool_format=tool_format,
        output_tool_schema_path=schema_path.root if schema_path else None,
        output_tool_write_frequency=WriteFrequency(write_freq.value) if write_freq else None,
        output_tool_batch_size=Integer(processing.output_batch_size.root) if write_freq and processing.output_batch_size else None,
        output_tool_file_path=output_file.root if output_file and name_known == OutputFileNameKnown.known else None,
        output_tool_directory_path=output_directory.root if output_directory else None,
        output_tool_name_needed=Boolean(True) if name_known in (OutputFileNameKnown.partially, OutputFileNameKnown.unknown) else None,
        output_tool_name_pattern=processing.output_file_name_template.root if name_known == OutputFileNameKnown.partially and processing.output_file_name_template else None,
    )
