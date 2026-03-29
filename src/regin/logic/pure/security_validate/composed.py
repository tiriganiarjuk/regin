"""Security validation composed functions — blocking security checks.

CC=4+. All three checks are CC=4-6.
Imports path_operations/simple (Composed can import Simple cross-module).

Three blocking checks that run before grant derivation in L3. A blocking
violation halts the pipeline — the agent definition must be fixed before
it can proceed. These checks enforce invariants that, if violated, would
produce ambiguous or dangerous permission states that grant derivation
cannot resolve safely.

All three checks examine path relationships in the security section.
They return lists of BlockingViolation — an empty list means the check
passed. The checks are independent and can run in any order.
"""

from regin.logic.pure.path_operations.simple import is_subpath, paths_overlap
from regin.structure.model.blocking_violation import BlockingCheck, BlockingViolation
from regin.structure.gen.schema.agent_paths_resolved import Security


def check_output_path_not_in_allowed_write(security: Security) -> list[BlockingViolation]:
    """Output path must not overlap with any allowed_write entry.

    Overlap would mean the agent could overwrite its own output through general
    write capability, bypassing the structured output tool. This is a security
    boundary: the output tool enforces format validation and naming rules that
    general write does not. If the paths overlap, there is no way to distinguish
    "write to output" (validated) from "write to allowed path" (unvalidated).
    """
    security_io = security.security_io
    output_path = security_io.io_output_file or security_io.io_output_directory
    if not output_path:
        return []
    allowed_write = security.security_paths.paths_allowed_write
    if not allowed_write:
        return []
    output = output_path.root
    violations: list[BlockingViolation] = []
    for write_path in allowed_write.root:
        write_path_str = write_path.root
        if paths_overlap(output, write_path_str):
            violations.append(BlockingViolation(
                check=BlockingCheck.output_path_in_allowed_write,
                message=f"output path {output} overlaps with allowed_write {write_path_str}",
                paths=(output, write_path_str),
            ))
    return violations


def check_tempdir_isolation(security: Security) -> list[BlockingViolation]:
    """Input tempdir and scratch tempdir must be different directories.

    If they collide, the agent's intermediate scratch writes could corrupt or
    interfere with its input data, and there would be no way to distinguish
    input reads from scratch reads in the permission model.
    """
    security_io = security.security_io
    if not security_io.io_input_tempdir or not security_io.io_scratch_tempdir:
        return []
    if security_io.io_input_tempdir.root == security_io.io_scratch_tempdir.root:
        return [BlockingViolation(
            check=BlockingCheck.tempdir_collision,
            message=f"input_tempdir and scratch_tempdir are both '{security_io.io_input_tempdir.root}'",
            paths=(security_io.io_input_tempdir.root, security_io.io_scratch_tempdir.root),
        )]
    return []


def check_scratch_not_in_output(security: Security) -> list[BlockingViolation]:
    """Scratch tempdir must not live inside the output directory.

    Otherwise, intermediate computation artifacts could be mistaken for final
    output, or the output tool's directory scanning could pick up scratch files
    as results. The scratch path is resolved to its full /tmp/{workspace}/
    form before the subpath check.
    """
    security_io = security.security_io
    if not security_io.io_scratch_tempdir or not security_io.io_output_directory:
        return []
    workspace_name = security.security_paths.paths_workspace.root.rstrip("/").rsplit("/", 1)[-1]
    scratch_path = f"/tmp/{workspace_name}/{security_io.io_scratch_tempdir.root}/"
    output_dir = security_io.io_output_directory.root
    if is_subpath(scratch_path, output_dir):
        return [BlockingViolation(
            check=BlockingCheck.scratch_overlaps_output,
            message=f"scratch path {scratch_path} is inside output directory {output_dir}",
            paths=(scratch_path, output_dir),
        )]
    return []
