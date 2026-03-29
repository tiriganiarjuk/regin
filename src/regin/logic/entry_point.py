"""Pipeline orchestration — run the full L0-L8 DAG.

Sequences individual branch orchestrators.
"""

from pathlib import Path

from loguru import logger

from regin.logic.orchestrate import (
    level0_defaults_inject,
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


def checkpoint(output_dir: Path, name: str) -> Path:
    """Return the path for a named checkpoint file."""
    return output_dir / f"{name}.toml"


def run_trunk(input_path: Path, output_dir: Path) -> Path:
    """L0-L2: inject defaults, resolve paths, verify paths."""
    logger.info("L0 defaults_inject")
    level0_defaults_inject.run(input_path, checkpoint(output_dir, "raw_definition_defaulted"))

    logger.info("L1 paths_resolve")
    level1_paths_resolve.run(checkpoint(output_dir, "raw_definition_defaulted"), checkpoint(output_dir, "paths_resolved"))

    logger.info("L2 paths_verify")
    level2_paths_verify.run(checkpoint(output_dir, "paths_resolved"), checkpoint(output_dir, "paths_verified"))
    return checkpoint(output_dir, "paths_verified")


def run_fanout(output_dir: Path) -> Path:
    """L3: four content reducers + permissions resolver (independent branches)."""
    logger.info("L3 content_instructions_reduce")
    level3_content_instructions_reduce.run(checkpoint(output_dir, "paths_verified"), checkpoint(output_dir, "instructions_reduced"))

    logger.info("L3 content_examples_reduce")
    level3_content_examples_reduce.run(checkpoint(output_dir, "paths_verified"), checkpoint(output_dir, "examples_reduced"))

    logger.info("L3 content_guardrails_reduce")
    level3_content_guardrails_reduce.run(checkpoint(output_dir, "paths_verified"), checkpoint(output_dir, "guardrails_reduced"))

    logger.info("L3 content_success_reduce")
    level3_content_success_reduce.run(checkpoint(output_dir, "paths_verified"), checkpoint(output_dir, "success_reduced"))

    logger.info("L3 permissions_resolve")
    level3_permissions_resolve.run(checkpoint(output_dir, "paths_verified"), checkpoint(output_dir, "permissions_resolved"))
    return checkpoint(output_dir, "permissions_resolved")


def run_convergence(output_dir: Path) -> Path:
    """L4-L8: merge branches, regroup, resolve to vendor format."""
    logger.info("L4 content_execution_merge")
    level4_content_execution_merge.run(
        checkpoint(output_dir, "instructions_reduced"), checkpoint(output_dir, "examples_reduced"), checkpoint(output_dir, "execution_merged"),
    )

    logger.info("L4 content_criteria_merge")
    level4_content_criteria_merge.run(
        checkpoint(output_dir, "guardrails_reduced"), checkpoint(output_dir, "success_reduced"), checkpoint(output_dir, "criteria_merged"),
    )

    logger.info("L5 content_includes_merge")
    level5_content_includes_merge.run(
        checkpoint(output_dir, "execution_merged"), checkpoint(output_dir, "criteria_merged"), checkpoint(output_dir, "includes_merged"),
    )

    logger.info("L6 universal_merge")
    level6_universal_merge.run(
        checkpoint(output_dir, "permissions_resolved"), checkpoint(output_dir, "includes_merged"), checkpoint(output_dir, "universal_format"),
    )

    logger.info("L7 render_regroup")
    level7_render_regroup.run(checkpoint(output_dir, "universal_format"), checkpoint(output_dir, "universal_render"))

    logger.info("L8 anthropic_resolve")
    level8_anthropic_resolve.run(checkpoint(output_dir, "universal_render"), checkpoint(output_dir, "anthropic_render"))
    return checkpoint(output_dir, "anthropic_render")


def run_pipeline(input_path: Path, output: Path | None) -> Path:
    """Run the full L0-L8 DAG pipeline. Returns path to final output."""
    resolved = input_path.resolve()
    output_dir = (output or resolved.parent / resolved.stem).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    run_trunk(resolved, output_dir)
    run_fanout(output_dir)
    return run_convergence(output_dir)
