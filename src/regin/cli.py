"""Regin CLI — run the full DAG pipeline.

Takes a raw agent definition TOML and resolves it through the gated
stages below into an anthropic_render.toml ready for Galdr.

Usage:
    regin /path/to/agent-definition.toml
    regin /path/to/agent-definition.toml -o /path/to/output-dir
"""

from pathlib import Path

import typer
from loguru import logger

from regin.logic.orchestrate.anthropic_resolve.orchestrate import run as run_anthropic_resolve
from regin.logic.orchestrate.content_merge.orchestrate import (
    run_criteria_merge,
    run_execution_merge,
    run_includes_merge,
)
from regin.logic.orchestrate.content_reduce.orchestrate import (
    run_examples,
    run_guardrails,
    run_instructions,
    run_success,
)
from regin.logic.orchestrate.defaults_inject.orchestrate import run as run_defaults_inject
from regin.logic.orchestrate.paths_resolve.orchestrate import run as run_paths_resolve
from regin.logic.orchestrate.paths_verify.orchestrate import run as run_paths_verify
from regin.logic.orchestrate.permissions_resolve.orchestrate import run as run_permissions_resolve
from regin.logic.orchestrate.render_regroup.orchestrate import run as run_render_regroup
from regin.logic.orchestrate.universal_merge.orchestrate import run as run_universal_merge

app = typer.Typer(help="Resolve agent definition TOML through the Regin DAG pipeline.")


def checkpoint(output_dir: Path, name: str) -> Path:
    """Return the path for a named checkpoint file."""
    return output_dir / f"{name}.toml"


def run_trunk(input_path: Path, output_dir: Path) -> Path:
    """L0-L2: inject defaults, resolve paths, verify paths."""
    logger.info("L0 defaults_inject")
    run_defaults_inject(input_path, checkpoint(output_dir, "raw_definition_defaulted"))

    logger.info("L1 paths_resolve")
    run_paths_resolve(checkpoint(output_dir, "raw_definition_defaulted"), checkpoint(output_dir, "paths_resolved"))

    logger.info("L2 paths_verify")
    run_paths_verify(checkpoint(output_dir, "paths_resolved"), checkpoint(output_dir, "paths_verified"))
    return checkpoint(output_dir, "paths_verified")


def run_fanout(output_dir: Path) -> Path:
    """L3: four content reducers + permissions resolver (independent branches)."""
    logger.info("L3 content_instructions_reduce")
    run_instructions(checkpoint(output_dir, "paths_verified"), checkpoint(output_dir, "instructions_reduced"))

    logger.info("L3 content_examples_reduce")
    run_examples(checkpoint(output_dir, "paths_verified"), checkpoint(output_dir, "examples_reduced"))

    logger.info("L3 content_guardrails_reduce")
    run_guardrails(checkpoint(output_dir, "paths_verified"), checkpoint(output_dir, "guardrails_reduced"))

    logger.info("L3 content_success_reduce")
    run_success(checkpoint(output_dir, "paths_verified"), checkpoint(output_dir, "success_reduced"))

    logger.info("L3 permissions_resolve")
    run_permissions_resolve(checkpoint(output_dir, "paths_verified"), checkpoint(output_dir, "permissions_resolved"))
    return checkpoint(output_dir, "permissions_resolved")


def run_convergence(output_dir: Path) -> Path:
    """L4-L8: merge branches, regroup, resolve to vendor format."""
    logger.info("L4 content_execution_merge")
    run_execution_merge(
        checkpoint(output_dir, "instructions_reduced"), checkpoint(output_dir, "examples_reduced"), checkpoint(output_dir, "execution_merged"),
    )

    logger.info("L4 content_criteria_merge")
    run_criteria_merge(
        checkpoint(output_dir, "guardrails_reduced"), checkpoint(output_dir, "success_reduced"), checkpoint(output_dir, "criteria_merged"),
    )

    logger.info("L5 content_includes_merge")
    run_includes_merge(
        checkpoint(output_dir, "execution_merged"), checkpoint(output_dir, "criteria_merged"), checkpoint(output_dir, "includes_merged"),
    )

    logger.info("L6 universal_merge")
    run_universal_merge(
        checkpoint(output_dir, "permissions_resolved"), checkpoint(output_dir, "includes_merged"), checkpoint(output_dir, "universal_format"),
    )

    logger.info("L7 render_regroup")
    run_render_regroup(checkpoint(output_dir, "universal_format"), checkpoint(output_dir, "universal_render"))

    logger.info("L8 anthropic_resolve")
    run_anthropic_resolve(checkpoint(output_dir, "universal_render"), checkpoint(output_dir, "anthropic_render"))
    return checkpoint(output_dir, "anthropic_render")


@app.command()
def run(
    input_path: Path = typer.Argument(help="Path to raw agent definition TOML"),
    output: Path | None = typer.Option(
        None, "-o", "--output",
        help="Output directory (default: sibling directory named after input stem)",
    ),
) -> None:
    """Run the full L0-L8 DAG pipeline."""
    resolved = input_path.resolve()
    output_dir = (output or resolved.parent / resolved.stem).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    run_trunk(resolved, output_dir)
    run_fanout(output_dir)
    result = run_convergence(output_dir)
    logger.success(f"Done: {result}")


def main() -> None:
    """Entry point for pyproject.toml."""
    app()
