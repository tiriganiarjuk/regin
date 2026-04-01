"""Merge content branches — execution, criteria, and final includes.

Three sequential merges converging the content branch:
L4 execution_merge: instructions + examples → execution
L4 criteria_merge:  guardrails + success → criteria
L5 includes_merge:  execution + criteria → includes (fully resolved content)
"""

from pathlib import Path

import gate_criteria_merged_input
import gate_criteria_merged_output
import gate_examples_reduced_input
import gate_execution_merged_input
import gate_execution_merged_output
import gate_guardrails_reduced_input
import gate_includes_merged_output
import gate_instructions_reduced_input
import gate_success_reduced_input

from regin.logic.impure.gates.simple import validate_input, validate_output
from regin.structure.gen.schema.agent_criteria_merged import AgentCriteriaMerged
from regin.structure.gen.schema.agent_examples_reduced import AgentExamplesReduced
from regin.structure.gen.schema.agent_execution_merged import AgentExecutionMerged
from regin.structure.gen.schema.agent_execution_merged import Criteria
from regin.structure.gen.schema.agent_guardrails_reduced import (
    AgentGuardrailsReduced,
    FailureCriteria,
    SuccessCriteria,
)
from regin.structure.gen.schema.agent_includes_merged import AgentIncludesMerged
from regin.structure.gen.schema.agent_instructions_reduced import (
    AgentInstructionsReduced,
    ExecutionExamples,
)
from regin.structure.gen.schema.agent_success_reduced import AgentSuccessReduced


def run_execution_merge(left_path: Path, right_path: Path, output_path: Path) -> str:
    """Merge instructions (left) and examples (right) into execution."""
    json_left = validate_input(gate_instructions_reduced_input, left_path)
    json_right = validate_input(gate_examples_reduced_input, right_path)
    left = AgentInstructionsReduced.model_validate_json(json_left)
    right = AgentExamplesReduced.model_validate_json(json_right)
    left.execution.execution_examples = ExecutionExamples.model_validate_json(
        right.execution.execution_examples.model_dump_json()
    )
    json_mutated = left.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    merged = AgentExecutionMerged.model_validate_json(json_mutated)
    json_out = merged.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    validate_output(gate_execution_merged_output, json_out, output_path)
    return json_out


def run_criteria_merge(left_path: Path, right_path: Path, output_path: Path) -> str:
    """Merge guardrails (left) and success/failure (right) into criteria."""
    json_left = validate_input(gate_guardrails_reduced_input, left_path)
    json_right = validate_input(gate_success_reduced_input, right_path)
    left = AgentGuardrailsReduced.model_validate_json(json_left)
    right = AgentSuccessReduced.model_validate_json(json_right)
    left.criteria.success_criteria = SuccessCriteria.model_validate_json(
        right.criteria.success_criteria.model_dump_json()
    )
    left.criteria.failure_criteria = FailureCriteria.model_validate_json(
        right.criteria.failure_criteria.model_dump_json()
    )
    json_mutated = left.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    merged = AgentCriteriaMerged.model_validate_json(json_mutated)
    json_out = merged.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    validate_output(gate_criteria_merged_output, json_out, output_path)
    return json_out


def run_includes_merge(left_path: Path, right_path: Path, output_path: Path) -> str:
    """Merge execution (left) and criteria (right) into fully resolved includes."""
    json_left = validate_input(gate_execution_merged_input, left_path)
    json_right = validate_input(gate_criteria_merged_input, right_path)
    left = AgentExecutionMerged.model_validate_json(json_left)
    right = AgentCriteriaMerged.model_validate_json(json_right)
    left.criteria = Criteria.model_validate_json(
        right.criteria.model_dump_json()
    )
    json_mutated = left.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    merged = AgentIncludesMerged.model_validate_json(json_mutated)
    json_out = merged.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    validate_output(gate_includes_merged_output, json_out, output_path)
    return json_out
