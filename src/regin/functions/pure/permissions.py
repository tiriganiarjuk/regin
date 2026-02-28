"""6-phase security resolution algorithm (A-F).

Transforms security + task.processing into enforcement grants
and an optional enforcement output tool.

Phases A-F are documented in SECURITY_RESOLUTION.md.
"""

from regin.structures.errors import BlockingCheckFailure
from regin.structures.paths_resolved import (
    Context,
    Processing,
    Security,
    SecurityCapabilities,
    SecurityIo,
    SecurityPaths,
    SecuritySchema,
)
from regin.structures.resolved_grants import OutputMode

READ_POSSIBLE = frozenset({"read", "search", "inspect"})
WRITE_POSSIBLE = frozenset({"read", "search", "inspect", "write", "edit", "append"})
ALL_CAPABILITIES = ("read", "search", "inspect", "write", "edit", "append")


def classify_output_mode(security_io: SecurityIo, processing: Processing) -> OutputMode:
    """Phase A: determine enforcement output mode from IO and format."""
    has_output = (
        security_io.security_io_output_file is not None
        or security_io.security_io_output_directory is not None
    )
    if not has_output:
        return OutputMode.none
    if processing.processing_output_file_format.value in ("json", "jsonl"):
        return OutputMode.enforced
    return OutputMode.grant_only


def get_output_path(security_io: SecurityIo) -> str | None:
    """Extract the output path from IO, whichever field is present."""
    if security_io.security_io_output_file is not None:
        return security_io.security_io_output_file.root
    if security_io.security_io_output_directory is not None:
        return security_io.security_io_output_directory.root
    return None


def is_subpath_of(child: str, parent: str) -> bool:
    """Check if child path starts with parent path."""
    return child.startswith(parent)


def check_blocking_constraints(
    security_io: SecurityIo,
    allowed_write: list[str],
) -> str:
    """Phase B: blocking checks. Raises BlockingCheckFailure or returns 'pass'."""
    output_path = get_output_path(security_io)
    if output_path is not None:
        for write_path in allowed_write:
            if is_subpath_of(output_path, write_path) or output_path == write_path:
                msg = f"output path {output_path} overlaps allowed_write {write_path}"
                raise BlockingCheckFailure(msg)
    input_tempdir = security_io.security_io_input_tempdir
    scratch_tempdir = security_io.security_io_scratch_tempdir
    if input_tempdir is not None and scratch_tempdir is not None:
        if input_tempdir.root == scratch_tempdir.root:
            msg = f"input_tempdir equals scratch_tempdir: {input_tempdir.root}"
            raise BlockingCheckFailure(msg)
    if scratch_tempdir is not None:
        output_dir = security_io.security_io_output_directory
        if output_dir is not None and is_subpath_of(scratch_tempdir.root, output_dir.root):
            msg = f"scratch_tempdir {scratch_tempdir.root} subpath of output_directory"
            raise BlockingCheckFailure(msg)
    return "pass"


def make_empty_grants() -> dict[str, set[str]]:
    """Create an empty capability-to-paths grant map."""
    return {cap: set() for cap in ALL_CAPABILITIES}


def extract_requested(capabilities: SecurityCapabilities) -> set[str]:
    """Extract requested capability names as a string set."""
    return {cap.value for cap in capabilities.security_capabilities_requested.root}


def extract_prohibited(capabilities: SecurityCapabilities) -> set[str]:
    """Extract prohibited capability names as a string set."""
    if capabilities.security_capabilities_prohibited is None:
        return set()
    return {cap.value for cap in capabilities.security_capabilities_prohibited.root}


def resolve_explicit_grants(
    paths: SecurityPaths,
    capabilities: SecurityCapabilities,
) -> dict[str, set[str]]:
    """Phase C: System 1 grants — capability intersection with prohibition."""
    requested = extract_requested(capabilities)
    prohibited = extract_prohibited(capabilities)
    grants = make_empty_grants()
    if paths.security_paths_allowed_read is not None:
        effective = READ_POSSIBLE & requested - prohibited
        for read_path in paths.security_paths_allowed_read.root:
            for capability in effective:
                grants[capability].add(read_path.root)
    if paths.security_paths_allowed_write is not None:
        effective = WRITE_POSSIBLE & requested - prohibited
        for write_path in paths.security_paths_allowed_write.root:
            for capability in effective:
                grants[capability].add(write_path.root)
    return grants


def build_tempdir_path(workspace: str, tempdir_name: str) -> str:
    """Build a /tmp/{workspace_basename}/{tempdir_name}/ path."""
    workspace_base = workspace.rstrip("/").rsplit("/", maxsplit=1)[-1]
    return f"/tmp/{workspace_base}/{tempdir_name}/"


def add_implicit_reads(
    grants: dict[str, set[str]],
    security_io: SecurityIo,
    schema: SecuritySchema,
    context: Context | None,
    workspace: str,
) -> dict[str, set[str]]:
    """Phase D read grants: input paths, schemas, context, tempdirs."""
    if security_io.security_io_input_file is not None:
        grants["read"].add(security_io.security_io_input_file.root)
    if security_io.security_io_input_directory is not None:
        grants["read"].add(security_io.security_io_input_directory.root)
    if schema.security_input_schema is not None:
        grants["read"].add(schema.security_input_schema.root)
    if schema.security_output_schema is not None:
        embed = schema.security_output_schema_embed
        if embed is None or embed.root is not True:
            grants["read"].add(schema.security_output_schema.root)
    if context is not None:
        if context.context_required is not None:
            for item in context.context_required.root:
                grants["read"].add(item.context_path.root)
        if context.context_available is not None:
            for item in context.context_available.root:
                grants["read"].add(item.context_path.root)
    if security_io.security_io_input_tempdir is not None:
        tempdir_path = build_tempdir_path(
            workspace, security_io.security_io_input_tempdir.root,
        )
        grants["read"].add(tempdir_path)
    return grants


def add_implicit_writes(
    grants: dict[str, set[str]],
    security_io: SecurityIo,
    workspace: str,
    mode: OutputMode,
    requested: set[str],
) -> dict[str, set[str]]:
    """Phase D write grants: scratch tempdir and text/markdown output."""
    if security_io.security_io_scratch_tempdir is not None:
        tempdir_path = build_tempdir_path(
            workspace, security_io.security_io_scratch_tempdir.root,
        )
        grants["write"].add(tempdir_path)
    if mode == OutputMode.grant_only:
        output_path = get_output_path(security_io)
        if output_path is not None:
            write_caps = {"write", "edit", "append"}
            for capability in ("write", "edit", "append"):
                if capability in requested & write_caps:
                    grants[capability].add(output_path)
                    break
    return grants


def collapse_grant_set(grants: dict[str, set[str]]) -> dict[str, list[str]]:
    """Phase E: deduplicate each capability bucket by path containment."""
    result: dict[str, list[str]] = {}
    for capability in ALL_CAPABILITIES:
        paths = sorted(grants[capability], key=len)
        kept: list[str] = []
        for path in paths:
            absorbed = any(
                is_subpath_of(path, ancestor)
                for ancestor in kept
                if ancestor != path
            )
            if not absorbed:
                kept.append(path)
        if kept:
            result[capability] = kept
    return result


def build_enforcement_tool(
    processing: Processing,
    security_io: SecurityIo,
    schema: SecuritySchema,
    mode: OutputMode,
) -> dict[str, str | int | bool] | None:
    """Phase F: build enforcement output tool when MODE is ENFORCED."""
    if mode != OutputMode.enforced:
        return None
    tool: dict[str, str | int | bool] = {
        "enforcement_output_tool_format": processing.processing_output_file_format.value,
        "enforcement_output_tool_schema_path": schema.security_output_schema.root,
    }
    if processing.processing_output_file_format.value == "jsonl":
        freq = processing.processing_output_write_frequency
        if freq is not None:
            tool["enforcement_output_tool_write_frequency"] = freq.value
            if freq.value == "batch" and processing.processing_output_batch_size is not None:
                tool["enforcement_output_tool_batch_size"] = (
                    processing.processing_output_batch_size.root
                )
    name_known = processing.processing_output_file_name_known.value
    if name_known == "known":
        tool["enforcement_output_tool_file_path"] = security_io.security_io_output_file.root
    elif name_known in ("partially", "unknown"):
        tool["enforcement_output_tool_directory_path"] = (
            security_io.security_io_output_directory.root
        )
        tool["enforcement_output_tool_name_needed"] = True
        if name_known == "partially":
            template = processing.processing_output_file_name_template
            if template is not None:
                tool["enforcement_output_tool_name_pattern"] = template.root
    return tool


def extract_allowed_write(paths: SecurityPaths) -> list[str]:
    """Extract allowed_write paths as plain strings."""
    if paths.security_paths_allowed_write is None:
        return []
    return [path.root for path in paths.security_paths_allowed_write.root]


def build_enforcement(
    security: Security,
    processing: Processing,
    context: Context | None,
) -> dict[str, dict[str, list[str]] | dict[str, str | int | bool] | None]:
    """Compose phases A-F into the enforcement section dict."""
    mode = classify_output_mode(security.security_io, processing)
    allowed_write = extract_allowed_write(security.security_paths)
    check_blocking_constraints(security.security_io, allowed_write)
    explicit = resolve_explicit_grants(
        security.security_paths, security.security_capabilities,
    )
    workspace = security.security_paths.security_paths_workspace.root
    requested = extract_requested(security.security_capabilities)
    implicit = make_empty_grants()
    add_implicit_reads(
        implicit, security.security_io,
        security.security_schema, context, workspace,
    )
    add_implicit_writes(
        implicit, security.security_io, workspace, mode, requested,
    )
    tool = build_enforcement_tool(
        processing, security.security_io, security.security_schema, mode,
    )
    result: dict[str, dict[str, list[str]] | dict[str, str | int | bool]] = {
        "enforcement_explicit_grants": collapse_grant_set(explicit),
        "enforcement_implicit_grants": collapse_grant_set(implicit),
    }
    if tool is not None:
        result["enforcement_output_tool"] = tool
    return result
