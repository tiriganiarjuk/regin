"""Regin — pipeline resolver CLI entry point.

Takes a raw agent definition TOML and resolves it through Nornir-gated
pipeline stages (levels 1-7) into a universal render TOML.

Sidecar directory default: same parent as input, stem of input filename.
"""

import argparse
from pathlib import Path

from loguru import logger

from regin.steps import (
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


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="regin",
        description="Resolve agent definitions through Nornir-gated pipeline stages",
    )
    parser.add_argument("input", help="Path to raw agent definition TOML")
    parser.add_argument("-o", "--output-dir", help="Output directory for intermediates")
    return parser


def run_pipeline(input_path: str, output_dir: str) -> str:
    """Run levels 1-8 of the pipeline. Returns final output path."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Level 1: resolve workspace-relative paths to absolute
    paths_resolved = level1_paths_resolve.run(
        input_path, str(out / "paths_resolved.toml"),
    )

    # Level 2: verify all absolute paths exist on disk
    paths_verified = level2_paths_verify.run(
        paths_resolved, str(out / "paths_verified.toml"),
    )

    # Level 3 content branch: four parallel reducers (run sequentially)
    instructions = level3_content_instructions_reduce.run(
        paths_verified, str(out / "instructions_reduced.toml"),
    )
    examples = level3_content_examples_reduce.run(
        paths_verified, str(out / "examples_reduced.toml"),
    )
    guardrails = level3_content_guardrails_reduce.run(
        paths_verified, str(out / "guardrails_reduced.toml"),
    )
    success = level3_content_success_reduce.run(
        paths_verified, str(out / "success_reduced.toml"),
    )

    # Level 3 permissions branch: security resolution
    permissions = level3_permissions_resolve.run(
        paths_verified, str(out / "permissions_resolved.toml"),
    )

    # Level 4: content merges
    execution = level4_content_execution_merge.run(
        instructions, examples, str(out / "execution_merged.toml"),
    )
    criteria = level4_content_criteria_merge.run(
        guardrails, success, str(out / "criteria_merged.toml"),
    )

    # Level 5: final content merge
    includes = level5_content_includes_merge.run(
        execution, criteria, str(out / "includes_merged.toml"),
    )

    # Level 6: convergence — content + permissions
    universal = level6_universal_merge.run(
        includes, permissions, str(out / "universal_format.toml"),
    )

    # Level 7: regroup domain sections into consumption sections
    render = level7_render_regroup.run(
        universal, str(out / "universal_render.toml"),
    )

    # Level 8: resolve to Anthropic platform render format
    return level8_anthropic_resolve.run(
        render, str(out / "anthropic_render.toml"),
    )


def main() -> int:
    """Entry point for the Regin CLI."""
    parser = build_parser()
    args = parser.parse_args()
    input_path = str(Path(args.input).resolve())
    output_dir = args.output_dir
    if output_dir is None:
        output_dir = str(Path(input_path).parent / Path(input_path).stem)
    logger.info("Regin: {} → {}", input_path, output_dir)
    run_pipeline(input_path, output_dir)
    logger.info("Pipeline complete: {}", output_dir)
    return 0
