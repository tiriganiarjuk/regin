"""Reduce content includes to inline entries.

Four parallel branches — instructions, examples, guardrails, success/failure.
Each reads paths_verified, walks the model tree to find include references,
resolves them to inline content, and writes a reduced checkpoint.
"""

from pathlib import Path

import gate_examples_reduced_output
import gate_guardrails_reduced_output
import gate_instructions_reduced_output
import gate_paths_verified_input
import gate_success_reduced_output

from regin.logic.impure.gates.simple import validate_input, validate_output
from regin.logic.impure.include_expand.assembled import (
    resolve_example_entry_include,
    resolve_example_group_include,
    resolve_failure_criteria_include,
    resolve_guardrails_anti_patterns_include,
    resolve_guardrails_constraints_include,
    resolve_instruction_include,
    resolve_success_criteria_include,
)
from regin.logic.impure.tree_mutate.assembled import walk_find_replace
from regin.logic.pure.tree_walk.composed import walk_and_find
from regin.structure.gen.schema.agent_examples_reduced import AgentExamplesReduced
from regin.structure.gen.schema.agent_guardrails_reduced import AgentGuardrailsReduced
from regin.structure.gen.schema.agent_instructions_reduced import AgentInstructionsReduced
from regin.structure.gen.schema.agent_paths_resolved import (
    AgentPathsResolved,
    IncludeExample,
    IncludeExampleGroup,
    IncludeFailureCriteria,
    IncludeGuardrailsAntiPatterns,
    IncludeGuardrailsConstraints,
    IncludeInstruction,
    IncludeSuccessCriteria,
)
from regin.structure.gen.schema.agent_success_reduced import AgentSuccessReduced


def run_instructions(input_path: Path, output_path: Path) -> str:
    """Reduce instruction includes to inline steps."""
    json_in = validate_input(gate_paths_verified_input, input_path)
    definition = AgentPathsResolved.model_validate_json(json_in)
    walk_find_replace(
        definition.execution.execution_instructions,
        IncludeInstruction,
        resolve_instruction_include,
        walk_and_find,
    )
    json_mutated = definition.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    reduced = AgentInstructionsReduced.model_validate_json(json_mutated)
    json_out = reduced.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    validate_output(gate_instructions_reduced_output, json_out, output_path)
    return json_out


def run_examples(input_path: Path, output_path: Path) -> str:
    """Reduce example includes — groups first, then entries within groups."""
    json_in = validate_input(gate_paths_verified_input, input_path)
    definition = AgentPathsResolved.model_validate_json(json_in)
    walk_find_replace(
        definition.execution.execution_examples,
        IncludeExampleGroup,
        resolve_example_group_include,
        walk_and_find,
    )
    walk_find_replace(
        definition.execution.execution_examples,
        IncludeExample,
        resolve_example_entry_include,
        walk_and_find,
    )
    json_mutated = definition.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    reduced = AgentExamplesReduced.model_validate_json(json_mutated)
    json_out = reduced.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    validate_output(gate_examples_reduced_output, json_out, output_path)
    return json_out


def run_guardrails(input_path: Path, output_path: Path) -> str:
    """Reduce guardrail includes to inline constraints and anti-patterns."""
    json_in = validate_input(gate_paths_verified_input, input_path)
    definition = AgentPathsResolved.model_validate_json(json_in)
    if definition.criteria.guardrails:
        walk_find_replace(
            definition.criteria.guardrails,
            IncludeGuardrailsConstraints,
            resolve_guardrails_constraints_include,
            walk_and_find,
        )
        walk_find_replace(
            definition.criteria.guardrails,
            IncludeGuardrailsAntiPatterns,
            resolve_guardrails_anti_patterns_include,
            walk_and_find,
        )
    json_mutated = definition.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    reduced = AgentGuardrailsReduced.model_validate_json(json_mutated)
    json_out = reduced.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    validate_output(gate_guardrails_reduced_output, json_out, output_path)
    return json_out


def run_success(input_path: Path, output_path: Path) -> str:
    """Reduce success and failure criteria includes to inline items."""
    json_in = validate_input(gate_paths_verified_input, input_path)
    definition = AgentPathsResolved.model_validate_json(json_in)
    walk_find_replace(
        definition.criteria.success_criteria,
        IncludeSuccessCriteria,
        resolve_success_criteria_include,
        walk_and_find,
    )
    walk_find_replace(
        definition.criteria.failure_criteria,
        IncludeFailureCriteria,
        resolve_failure_criteria_include,
        walk_and_find,
    )
    json_mutated = definition.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    reduced = AgentSuccessReduced.model_validate_json(json_mutated)
    json_out = reduced.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)
    validate_output(gate_success_reduced_output, json_out, output_path)
    return json_out
