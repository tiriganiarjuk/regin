"""Phase B blocking checks for security resolution.

Three pass/fail gates that reject definitions with conflicting path declarations.
Empty list means all checks passed. Non-empty blocks the DAG.

Pure — reads typed models, returns violation list.
"""

from regin.functions.pure.path_operations import is_subpath, paths_overlap
from regin.structures.blocking_violation import BlockingCheck, BlockingViolation
from regin.structures.schema.agent_paths_resolved import Security


def check_output_path_not_in_allowed_write(security: Security) -> list[BlockingViolation]:
    """Output path must not overlap with any allowed_write entry."""
    io = security.security_io
    output_path = io.io_output_file or io.io_output_directory
    if not output_path:
        return []
    allowed_write = security.security_paths.paths_allowed_write
    if not allowed_write:
        return []
    output = output_path.root
    violations: list[BlockingViolation] = []
    for write_path in allowed_write.root:
        wp = write_path.root
        if paths_overlap(output, wp):
            violations.append(BlockingViolation(
                check=BlockingCheck.output_path_in_allowed_write,
                message=f"output path {output} overlaps with allowed_write {wp}",
                paths=(output, wp),
            ))
    return violations


def check_tempdir_isolation(security: Security) -> list[BlockingViolation]:
    """Input tempdir and scratch tempdir must not collide."""
    io = security.security_io
    if not io.io_input_tempdir or not io.io_scratch_tempdir:
        return []
    if io.io_input_tempdir.root == io.io_scratch_tempdir.root:
        return [BlockingViolation(
            check=BlockingCheck.tempdir_collision,
            message=f"input_tempdir and scratch_tempdir are both '{io.io_input_tempdir.root}'",
            paths=(io.io_input_tempdir.root, io.io_scratch_tempdir.root),
        )]
    return []


def check_scratch_not_in_output(security: Security) -> list[BlockingViolation]:
    """Scratch tempdir path must not be a subpath of output directory."""
    io = security.security_io
    if not io.io_scratch_tempdir or not io.io_output_directory:
        return []
    workspace_name = security.security_paths.paths_workspace.root.rstrip("/").rsplit("/", 1)[-1]
    scratch_path = f"/tmp/{workspace_name}/{io.io_scratch_tempdir.root}/"
    output_dir = io.io_output_directory.root
    if is_subpath(scratch_path, output_dir):
        return [BlockingViolation(
            check=BlockingCheck.scratch_overlaps_output,
            message=f"scratch path {scratch_path} is inside output directory {output_dir}",
            paths=(scratch_path, output_dir),
        )]
    return []


def check_blocking(security: Security) -> list[BlockingViolation]:
    """Run all Phase B blocking checks. Empty list means pass."""
    return (
        check_output_path_not_in_allowed_write(security)
        + check_tempdir_isolation(security)
        + check_scratch_not_in_output(security)
    )
