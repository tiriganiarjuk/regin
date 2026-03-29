"""Regin CLI — run the full DAG pipeline.

Takes a raw agent definition TOML and resolves it through 13 gated
stages into an anthropic_render.toml ready for Galdr.

Usage:
    regin /path/to/agent-definition.toml
    regin /path/to/agent-definition.toml -o /path/to/output-dir
"""

from pathlib import Path

import typer
from loguru import logger

from regin.logic.entry_point import run_pipeline

app = typer.Typer(help="Resolve agent definition TOML through the Regin DAG pipeline.")


@app.command()
def run(
    input_path: Path = typer.Argument(help="Path to raw agent definition TOML"),
    output: Path | None = typer.Option(
        None, "-o", "--output",
        help="Output directory (default: sibling directory named after input stem)",
    ),
) -> None:
    """Run the full L0-L8 DAG pipeline."""
    result = run_pipeline(input_path, output)
    logger.success(f"Done: {result}")


def main() -> None:
    """Entry point for pyproject.toml."""
    app()
