"""Pipeline orchestration — run the full L1-L8 DAG.

Impure: each branch calls gates that perform file IO.
"""

from pathlib import Path

from loguru import logger

from regin.branches import (
    level1_paths_resolve,
    level2_paths_verify,
    level3_content_examples_reduce,
    level3_content_guardrails_reduce,
    level3_content_instructions_reduce,
    level3_content_success_reduce,
    level3_permissions_resolve,
    level4_content_criteria_merge,
    level4_content_execution_merge,
    level5_content_includes_merge,
    level6_universal_merge,
    level7_render_regroup,
    level8_anthropic_resolve,
)

CHECKPOINT_NAMES = (
    "paths_resolved",
    "paths_verified",
    "instructions_reduced",
    "examples_reduced",
    "guardrails_reduced",
    "success_reduced",
    "permissions_resolved",
    "execution_merged",
    "criteria_merged",
    "includes_merged",
    "universal_format",
    "universal_render",
    "anthropic_render",
)


def checkpoint(output_dir: Path, name: str) -> Path:
    """Return the path for a named checkpoint file."""
    return output_dir / f"{name}.toml"


def run_pipeline(input_path: Path, output_dir: Path) -> Path:
    """Run the full L1-L8 DAG pipeline. Returns path to anthropic_render.toml."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cp = lambda name: checkpoint(output_dir, name)

    logger.info("L1 paths_resolve")
    level1_paths_resolve.run(input_path, cp("paths_resolved"))

    logger.info("L2 paths_verify")
    level2_paths_verify.run(cp("paths_resolved"), cp("paths_verified"))

    logger.info("L3 content_instructions_reduce")
    level3_content_instructions_reduce.run(cp("paths_verified"), cp("instructions_reduced"))

    logger.info("L3 content_examples_reduce")
    level3_content_examples_reduce.run(cp("paths_verified"), cp("examples_reduced"))

    logger.info("L3 content_guardrails_reduce")
    level3_content_guardrails_reduce.run(cp("paths_verified"), cp("guardrails_reduced"))

    logger.info("L3 content_success_reduce")
    level3_content_success_reduce.run(cp("paths_verified"), cp("success_reduced"))

    logger.info("L3 permissions_resolve")
    level3_permissions_resolve.run(cp("paths_verified"), cp("permissions_resolved"))

    logger.info("L4 content_execution_merge")
    level4_content_execution_merge.run(
        cp("instructions_reduced"), cp("examples_reduced"), cp("execution_merged"),
    )

    logger.info("L4 content_criteria_merge")
    level4_content_criteria_merge.run(
        cp("guardrails_reduced"), cp("success_reduced"), cp("criteria_merged"),
    )

    logger.info("L5 content_includes_merge")
    level5_content_includes_merge.run(
        cp("execution_merged"), cp("criteria_merged"), cp("includes_merged"),
    )

    logger.info("L6 universal_merge")
    level6_universal_merge.run(
        cp("permissions_resolved"), cp("includes_merged"), cp("universal_format"),
    )

    logger.info("L7 render_regroup")
    level7_render_regroup.run(cp("universal_format"), cp("universal_render"))

    logger.info("L8 anthropic_resolve")
    level8_anthropic_resolve.run(cp("universal_render"), cp("anthropic_render"))

    return cp("anthropic_render")
