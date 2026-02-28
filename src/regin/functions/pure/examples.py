"""Reduce example includes at group and entry level.

Include gates return JSON: group gate returns an ExampleGroup object,
entry gate returns an array of ExampleEntry objects.
"""

import json

from regin.functions.pure.path_resolver import extract_str
from regin.structures.paths_resolved import (
    ExampleEntries,
    ExampleEntry,
    ExampleGroup,
    ExecutionExamples,
    IncludeExample,
    IncludeExampleGroup,
)


def parse_example_group(content: str) -> ExampleGroup:
    """Parse gate JSON into a validated ExampleGroup."""
    return ExampleGroup.model_validate(json.loads(content))


def parse_example_entries(content: str) -> list[ExampleEntry]:
    """Parse gate JSON into validated ExampleEntry items."""
    return [ExampleEntry.model_validate(entry) for entry in json.loads(content)["items"]]


def reduce_entry_includes(
    entries: list[ExampleEntry | IncludeExample], include_data: dict[str, str],
) -> list[ExampleEntry]:
    """Replace entry-level includes with inline ExampleEntry items."""
    result: list[ExampleEntry] = []
    for entry in entries:
        if not isinstance(entry, IncludeExample):
            result.append(entry)
            continue
        result.extend(parse_example_entries(include_data[extract_str(entry.include)]))
    return result


def reduce_examples(
    examples: ExecutionExamples, include_data: dict[str, str],
) -> list[ExampleGroup]:
    """Replace all include references with inline example groups and entries."""
    result: list[ExampleGroup] = []
    for group in examples.root:
        if isinstance(group, IncludeExampleGroup):
            result.append(parse_example_group(include_data[extract_str(group.include)]))
        elif isinstance(group, ExampleGroup) and group.example_entries:
            expanded = reduce_entry_includes(
                group.example_entries.root, include_data,
            )
            result.append(group.model_copy(update={
                "example_entries": ExampleEntries(root=expanded),
            }))
        else:
            result.append(group)
    return result
