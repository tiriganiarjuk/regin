"""Security validation assembled — Phase B blocking check wiring.

CC=1-2. Imports from composed within this module.

Thin assembly that runs all three blocking checks as a flat list. An empty
return list means all checks passed and grant derivation may proceed. A
non-empty list causes L3 to raise ValueError, halting the pipeline with
diagnostic messages for each violation.
"""

from regin.logic.pure.security_validate.composed import (
    check_output_path_not_in_allowed_write,
    check_scratch_not_in_output,
    check_tempdir_isolation,
)
from regin.structure.model.blocking_violation import BlockingViolation
from regin.structure.gen.schema.agent_paths_resolved import Security


def check_blocking(security: Security) -> list[BlockingViolation]:
    """Run all Phase B blocking checks. Empty list = all passed, proceed to grants.

    The three checks are independent — each examines a different path
    relationship invariant. All violations are collected, not short-circuited,
    so the author sees every problem in one pass.
    """
    return (
        check_output_path_not_in_allowed_write(security)
        + check_tempdir_isolation(security)
        + check_scratch_not_in_output(security)
    )
