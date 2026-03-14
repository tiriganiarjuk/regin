"""Regin CLI — run the full DAG pipeline.

Takes a raw agent definition TOML and resolves it through 13 gated
stages into an anthropic_render.toml ready for Galdr.

Usage:
    regin /path/to/agent-definition.toml
    regin /path/to/agent-definition.toml -o /path/to/output-dir
"""

import argparse
import sys
from pathlib import Path

from loguru import logger
from pydantic import ValidationError

from regin.functions.impure.pipeline import run_pipeline


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        prog="regin",
        description="Resolve agent definition TOML through the Regin DAG pipeline.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to raw agent definition TOML",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output directory (default: sibling directory named after input stem)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    args = parse_args(argv)
    input_path = args.input.resolve()

    if not input_path.exists():
        logger.error(f"Input not found: {input_path}")
        return 1

    output_dir = args.output or input_path.parent / input_path.stem
    output_dir = output_dir.resolve()

    logger.info(f"Input:  {input_path}")
    logger.info(f"Output: {output_dir}")

    try:
        result = run_pipeline(input_path, output_dir)
    except (ValueError, ImportError, ValidationError) as e:
        logger.error(f"Pipeline failed: {e}")
        return 1

    logger.success(f"Done: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
