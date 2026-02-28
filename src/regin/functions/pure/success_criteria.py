"""Reduce success/failure criteria includes to inline items.

Include gates return JSON arrays of criterion objects with
definition and evidence fields.
"""

import json

from regin.functions.pure.path_resolver import extract_str
from regin.structures.paths_resolved import (
    FailureCriteria,
    FailureItem,
    IncludeFailureCriteria,
    IncludeSuccessCriteria,
    SuccessCriteria,
    SuccessItem,
)


def parse_success_items(content: str) -> list[SuccessItem]:
    """Parse gate JSON into validated SuccessItem list."""
    return [SuccessItem.model_validate(entry) for entry in json.loads(content)["items"]]


def parse_failure_items(content: str) -> list[FailureItem]:
    """Parse gate JSON into validated FailureItem list."""
    return [FailureItem.model_validate(entry) for entry in json.loads(content)["items"]]


def reduce_success_criteria(
    criteria: SuccessCriteria, include_data: dict[str, str],
) -> list[SuccessItem]:
    """Replace success criteria includes with inline SuccessItem entries."""
    result: list[SuccessItem] = []
    for item in criteria.root:
        if isinstance(item, IncludeSuccessCriteria):
            result.extend(parse_success_items(include_data[extract_str(item.include)]))
        else:
            result.append(item)
    return result


def reduce_failure_criteria(
    criteria: FailureCriteria, include_data: dict[str, str],
) -> list[FailureItem]:
    """Replace failure criteria includes with inline FailureItem entries."""
    result: list[FailureItem] = []
    for item in criteria.root:
        if isinstance(item, IncludeFailureCriteria):
            result.extend(parse_failure_items(include_data[extract_str(item.include)]))
        else:
            result.append(item)
    return result
