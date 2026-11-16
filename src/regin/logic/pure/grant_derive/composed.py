"""Derive implicit grant sources and assemble output tool specification.

CC=4+. Import from simple within this module.

"Implicit" means these grants are NOT from the capabilities_requested field —
they are inferred from IO, schema, and context declarations that require file
access to function. An agent that declares io_input_file needs read access to
that file regardless of whether it requested "read" capability. Implicit grants
cover this: the pipeline infers the minimum permissions the agent needs to
operate, separate from what it explicitly asked for.

The output tool spec translates processing requirements (format, write frequency,
naming convention) into the enforcement model that will be matched against the
tool registry in L8 to find the binary that handles the agent's file output.
"""

from regin.structure.gen.schema.agent_paths_resolved import (
    Capabilities,
    Context,
    Processing,
    Security,
    SecurityIo,
    SecuritySchema,
)
from regin.structure.gen.schema.agent_permissions_resolved import (
    Boolean,
    EnforcementOutputTool,
    Integer,
    OutputFileNameKnown,
    OutputFormatKind,
    WriteFrequency,
)


# -- Capability extraction (CC=4) --

def extract_prohibited(caps: Capabilities | None) -> set[Capabilities]:
    """Extract the author's explicitly excluded capabilities.

    Prohibited capabilities subtract from the requested set before intersection,
    ensuring that even if a path is declared, a prohibited capability cannot be
    granted on it. This is the negative permission mechanism: the author says
    "I do NOT want edit capability even though my paths would allow it."
    """
    return {Capabilities(capability.value) for capability in caps.capabilities_prohibited.root} if caps and caps.capabilities_prohibited else set()


# -- Implicit source collectors (CC=4-5) --
# Each collector gathers read or write paths from one declaration domain
# (IO, schema, context). The union of all collectors forms the implicit
# read/write surface that the agent needs to function.

def collect_io_reads(security_io: SecurityIo, workspace_name: str) -> set[str]:
    """Collect implicit read paths from IO declarations.

    IO declarations that reference files (input_file, input_directory,
    input_tempdir, scratch_tempdir) generate implicit read grants. The agent
    must be able to read its own input — this is not a capability the author
    "requests" but a consequence of the IO contract. Scratch dirs also get
    read grants because the agent may need to re-read intermediate results.
    """
    reads: set[str] = set()
    if security_io.io_input_file:
        reads.add(security_io.io_input_file.root)
    if security_io.io_input_directory:
        reads.add(security_io.io_input_directory.root)
    if security_io.io_input_tempdir:
        reads.add(f"/tmp/{workspace_name}/{security_io.io_input_tempdir.root}/")
    if security_io.io_scratch_tempdir:
        reads.add(f"/tmp/{workspace_name}/{security_io.io_scratch_tempdir.root}/")
    return reads


def collect_schema_reads(schema: SecuritySchema) -> set[str]:
    """Collect implicit read paths from schema declarations.

    Schema files (input_schema, output_schema) need read grants so the agent
    can validate data against them at runtime. The output_schema read grant is
    suppressed when output_schema_embed is True, because embedded schemas are
    inlined into the prompt during rendering and don't require file access.
    """
    reads: set[str] = set()
    if schema.input_schema:
        reads.add(schema.input_schema.root)
    if schema.output_schema:
        embed = schema.output_schema_embed
        if not embed or not embed.root:
            reads.add(schema.output_schema.root)
    return reads


def collect_context_reads(context: Context) -> set[str]:
    """Collect implicit read paths from context resource declarations.

    Both required and available contexts generate read grants — the distinction
    between required/available is about error handling (missing required context
    is fatal to the agent), not about permission level. All declared context
    resources get the same read access.
    """
    reads: set[str] = set()
    if context.context_required:
        for item in context.context_required.root:
            reads.add(item.context_path.root)
    if context.context_available:
        for item in context.context_available.root:
            reads.add(item.context_path.root)
    return reads




# -- Output tool assembly --
# The output tool spec tells L8's tool registry matcher what kind of output
# tool binary to use. It encodes: format (json/jsonl), naming convention
# (known/partially/unknown), write frequency (single/batch), and paths.

def resolve_name_fields(
    name_known: OutputFileNameKnown,
    output_file: str | None,
    name_template: str | None,
) -> dict[str, Boolean | str | None]:
    """Resolve output tool name-related fields based on the name_known enum.

    The three OutputFileNameKnown states activate different field combinations:
    - known: output path is fixed (file_path set, name_needed false)
    - partially: naming pattern constrains the name (name_needed true, pattern set)
    - unknown: agent must determine filename at runtime (name_needed true, no pattern)
    """
    return {
        "output_tool_file_path": output_file if output_file and name_known == OutputFileNameKnown.known else None,
        "output_tool_name_needed": Boolean(True) if name_known in (OutputFileNameKnown.partially, OutputFileNameKnown.unknown) else None,
        "output_tool_name_pattern": name_template if name_known == OutputFileNameKnown.partially and name_template else None,
    }


def resolve_write_fields(
    write_freq: WriteFrequency | None,
    batch_size: int | None,
) -> dict[str, WriteFrequency | Integer | None]:
    """Resolve write frequency and batch size fields.

    Batch size is only meaningful when write_frequency is "batch" — for single
    writes or streaming, it is forced to None regardless of what the author
    declared. This prevents confusing the tool registry matcher.
    """
    return {
        "output_tool_write_frequency": write_freq,
        "output_tool_batch_size": Integer(batch_size) if write_freq and write_freq.value == "batch" and batch_size else None,
    }


def prepare_tool_fields(
    security: Security,
    processing: Processing,
) -> dict[str, WriteFrequency | int | str | None]:
    """Extract and normalize raw fields for output tool assembly.

    Gathers the scattered source fields (IO paths, schema paths, processing
    config) into a flat dict that assemble_output_tool can destructure.
    Each field is independently nullable — the output tool spec is sparse,
    containing only the fields relevant to this agent's output configuration.
    """
    security_io = security.security_io
    schema = security.security_schema.output_schema
    return {
        "output_file": security_io.io_output_file.root if security_io.io_output_file else None,
        "output_directory": security_io.io_output_directory.root if security_io.io_output_directory else None,
        "schema_path": schema.root if schema else None,
        "name_template": processing.output_file_name_template.root if processing.output_file_name_template else None,
        "write_freq": WriteFrequency(processing.output_write_frequency.value) if processing.output_write_frequency else None,
        "batch_size": processing.output_batch_size.root if processing.output_write_frequency and processing.output_batch_size else None,
    }


def assemble_output_tool(
    security: Security,
    processing: Processing,
) -> EnforcementOutputTool | None:
    """Assemble the output tool enforcement spec from security and processing fields.

    Returns None for two distinct reasons:
    1. No output path declared — the agent doesn't produce file output.
    2. Output format is text/markdown — these formats don't need a structured
       output tool because they write via standard text output.

    This None propagates through the pipeline and means "no custom output tool
    in hooks" — the agent writes through general-purpose file tools instead.
    """
    security_io = security.security_io
    if not security_io.io_output_file and not security_io.io_output_directory:
        return None
    tool_format = OutputFormatKind(processing.output_file_format.value)
    if tool_format in (OutputFormatKind.text, OutputFormatKind.markdown):
        return None
    prepared = prepare_tool_fields(security, processing)
    name_known = OutputFileNameKnown(processing.output_file_name_known.value)
    return EnforcementOutputTool(
        output_tool_format=tool_format,
        output_tool_schema_path=prepared["schema_path"],
        output_tool_directory_path=prepared["output_directory"],
        **resolve_name_fields(name_known, prepared["output_file"], prepared["name_template"]),
        **resolve_write_fields(prepared["write_freq"], prepared["batch_size"]),
    )
