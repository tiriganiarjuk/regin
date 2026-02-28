"""Merge functions for DAG convergence steps.

All merges work at JSON level: verify shared sections match,
then combine branch-specific sections from each input.
"""

import json

from regin.functions.pure.section_compare import verify_sections_match

SHARED_CONTENT = ("indirect", "task", "security")


def merge_execution(
    instructions_json: str,
    examples_json: str,
) -> str:
    """Merge instructions-reduced + examples-reduced -> execution-merged."""
    verify_sections_match(instructions_json, examples_json, list(SHARED_CONTENT))
    base = json.loads(instructions_json)
    donor = json.loads(examples_json)
    base["execution"]["execution_examples"] = donor["execution"]["execution_examples"]
    return json.dumps(base)


def merge_criteria(
    guardrails_json: str,
    success_json: str,
) -> str:
    """Merge guardrails-reduced + success-reduced -> criteria-merged."""
    verify_sections_match(guardrails_json, success_json, list(SHARED_CONTENT))
    base = json.loads(guardrails_json)
    donor = json.loads(success_json)
    base["criteria"]["success_criteria"] = donor["criteria"]["success_criteria"]
    base["criteria"]["failure_criteria"] = donor["criteria"]["failure_criteria"]
    return json.dumps(base)


def merge_includes(
    execution_json: str,
    criteria_json: str,
) -> str:
    """Merge execution-merged + criteria-merged -> includes-merged."""
    verify_sections_match(execution_json, criteria_json, list(SHARED_CONTENT))
    base = json.loads(execution_json)
    donor = json.loads(criteria_json)
    base["criteria"] = donor["criteria"]
    return json.dumps(base)


def merge_universal(
    content_json: str,
    permissions_json: str,
) -> str:
    """Merge includes-merged + permissions-resolved -> universal-format."""
    verify_sections_match(content_json, permissions_json, list(SHARED_CONTENT))
    base = json.loads(content_json)
    donor = json.loads(permissions_json)
    base["enforcement"] = donor["enforcement"]
    return json.dumps(base)
