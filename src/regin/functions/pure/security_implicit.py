"""Derive implicit grants from structural declarations.

Walks security model fields and collects minimum-privilege paths.
No intersection with requested capabilities — purely structural.

Pure — reads typed models, returns typed model.
"""

from regin.functions.pure.path_operations import collapse_path_containment
from regin.structures.schema.agent_paths_resolved import Context, Security, SecurityIo, SecuritySchema
from regin.structures.schema.agent_permissions_resolved import (
    EnforcementImplicitEdit,
    EnforcementImplicitGrants,
    EnforcementImplicitRead,
    EnforcementImplicitWrite,
)


def collect_io_reads(io_section: SecurityIo, workspace_name: str) -> set[str]:
    """Collect read paths from IO declarations."""
    reads: set[str] = set()
    if io_section.io_input_file:
        reads.add(io_section.io_input_file.root)
    if io_section.io_input_directory:
        reads.add(io_section.io_input_directory.root)
    if io_section.io_input_tempdir:
        reads.add(f"/tmp/{workspace_name}/{io_section.io_input_tempdir.root}/")
    if io_section.io_scratch_tempdir:
        reads.add(f"/tmp/{workspace_name}/{io_section.io_scratch_tempdir.root}/")
    return reads


def collect_schema_reads(schema: SecuritySchema) -> set[str]:
    """Collect read paths from schema declarations."""
    reads: set[str] = set()
    if schema.input_schema:
        reads.add(schema.input_schema.root)
    if schema.output_schema:
        embed = schema.output_schema_embed
        if not embed or not embed.root:
            reads.add(schema.output_schema.root)
    return reads


def collect_context_reads(context: Context) -> set[str]:
    """Collect read paths from context declarations."""
    reads: set[str] = set()
    if context.context_required:
        for item in context.context_required.root:
            reads.add(item.context_path.root)
    if context.context_available:
        for item in context.context_available.root:
            reads.add(item.context_path.root)
    return reads


def collect_implicit_writes(io_section: SecurityIo, workspace_name: str) -> set[str]:
    """Collect write paths from scratch declarations."""
    writes: set[str] = set()
    if io_section.io_scratch_tempdir:
        writes.add(f"/tmp/{workspace_name}/{io_section.io_scratch_tempdir.root}/")
    return writes


def derive_implicit_grants(security: Security) -> EnforcementImplicitGrants:
    """Combine all implicit read/write sources into typed grant model."""
    workspace_name = security.security_paths.paths_workspace.root.rstrip("/").rsplit("/", 1)[-1]
    reads = (
        collect_io_reads(security.security_io, workspace_name)
        | collect_schema_reads(security.security_schema)
        | (collect_context_reads(security.context) if security.context else set())
    )
    writes = collect_implicit_writes(security.security_io, workspace_name)
    raw_grants: dict[str, set[str]] = {}
    if reads:
        raw_grants["read"] = reads
    if writes:
        raw_grants["write"] = writes
    collapsed = collapse_path_containment(raw_grants)
    return EnforcementImplicitGrants(
        read=EnforcementImplicitRead(collapsed["read"]) if "read" in collapsed else None,
        write=EnforcementImplicitWrite(collapsed["write"]) if "write" in collapsed else None,
        edit=EnforcementImplicitEdit(collapsed["edit"]) if "edit" in collapsed else None,
    )
