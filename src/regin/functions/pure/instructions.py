"""Reduce instruction includes to inline InstructionStep entries.

Include gate returns a JSON array of {instruction_mode, instruction_text}.
"""

import json

from regin.functions.pure.path_resolver import extract_str
from regin.structures.paths_resolved import (
    ExecutionInstructions,
    IncludeInstruction,
    InstructionStep,
)


def parse_instruction_entries(content: str) -> list[InstructionStep]:
    """Parse gate JSON into validated InstructionStep items."""
    return [InstructionStep.model_validate(entry) for entry in json.loads(content)["items"]]


def reduce_instructions(
    items: ExecutionInstructions, include_data: dict[str, str],
) -> list[InstructionStep]:
    """Replace include references with inline instruction steps."""
    result: list[InstructionStep] = []
    for item in items.root:
        if not isinstance(item, IncludeInstruction):
            result.append(item)
            continue
        result.extend(parse_instruction_entries(include_data[extract_str(item.include)]))
    return result
