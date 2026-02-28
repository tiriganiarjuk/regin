"""Reduce guardrail includes to inline string arrays.

Include gates return a JSON array of strings.
"""

import json

from regin.functions.pure.path_resolver import extract_str
from regin.structures.paths_resolved import (
    Guardrails,
    GuardrailsAntiPatterns,
    GuardrailsConstraints,
)


def parse_guardrail_items(content: str) -> list[str]:
    """Parse gate JSON into a list of guardrail strings."""
    return json.loads(content)["items"]


def reduce_guardrails(
    guardrails: Guardrails, include_data: dict[str, str],
) -> Guardrails:
    """Replace include references with inline string arrays."""
    updates: dict[str, list[str] | None] = {}

    if guardrails.include_guardrails_constraints:
        path = extract_str(guardrails.include_guardrails_constraints.include)
        updates["guardrails_constraints"] = GuardrailsConstraints(
            root=parse_guardrail_items(include_data[path]),
        )
        updates["include_guardrails_constraints"] = None

    if guardrails.include_guardrails_anti_patterns:
        path = extract_str(guardrails.include_guardrails_anti_patterns.include)
        updates["guardrails_anti_patterns"] = GuardrailsAntiPatterns(
            root=parse_guardrail_items(include_data[path]),
        )
        updates["include_guardrails_anti_patterns"] = None

    return guardrails.model_copy(update=updates) if updates else guardrails
