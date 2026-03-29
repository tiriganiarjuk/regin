"""Include expand assembled — concrete resolve callbacks for walk_find_replace.

CC=1-2. Each callback wires a specific gate+model to a generic expand function.
Imports from simple (within module) and tree_mutate/simple (Assembled->Simple).

Seven concrete include resolution callbacks, each wiring a specific gate module
and Pydantic model type to one of the three generic expansion strategies
(splice, replace, field). These are the callbacks passed to walk_find_replace
in the L3 content reducers.

Each function is named resolve_*_include to mirror the include type it handles.
The seven include types cover all external content references in the agent
definition: instructions, example groups, example entries, guardrails
constraints, guardrails anti-patterns, success criteria, failure criteria.
"""

import gate_include_example_entries_input
import gate_include_example_group_input
import gate_include_execution_instructions_input
import gate_include_failure_criteria_input
import gate_include_guardrails_anti_patterns_input
import gate_include_guardrails_constraints_input
import gate_include_success_criteria_input

from regin.logic.impure.include_expand.simple import (
    expand_field,
    expand_replace,
    expand_splice,
)
from regin.logic.impure.tree_mutate.simple import replace_found
from regin.structure.model.found_item import FoundItem
from regin.structure.gen.fragment.example_entries import (
    ExampleEntries as IncludeExampleEntriesModel,
)
from regin.structure.gen.fragment.example_group import (
    ExampleGroup as IncludeExampleGroupModel,
)
from regin.structure.gen.fragment.execution_instructions import (
    ExecutionInstructions as IncludeInstructionsModel,
)
from regin.structure.gen.fragment.failure_criteria import (
    FailureCriteria as IncludeFailureModel,
)
from regin.structure.gen.fragment.guardrails_anti_patterns import (
    GuardrailsAntiPatterns as IncludeAntiPatternsModel,
)
from regin.structure.gen.fragment.guardrails_constraints import (
    GuardrailsConstraints as IncludeConstraintsModel,
)
from regin.structure.gen.fragment.success_criteria import (
    SuccessCriteria as IncludeSuccessModel,
)
from regin.structure.gen.schema.agent_paths_resolved import (
    ExampleEntry,
    ExampleGroup,
    FailureItem,
    GuardrailsAntiPatterns,
    GuardrailsConstraints,
    IncludeExample,
    IncludeExampleGroup,
    IncludeFailureCriteria,
    IncludeGuardrailsAntiPatterns,
    IncludeGuardrailsConstraints,
    IncludeInstruction,
    IncludeSuccessCriteria,
    InstructionStep,
    SuccessItem,
)


def resolve_instruction_include(found: FoundItem[IncludeInstruction]) -> bool:
    """Load instruction include and splice steps into list."""
    return expand_splice(found, gate_include_execution_instructions_input, IncludeInstructionsModel, InstructionStep)


def resolve_example_group_include(found: FoundItem[IncludeExampleGroup]) -> bool:
    """Load example group include and replace 1:1."""
    return expand_replace(found, gate_include_example_group_input, IncludeExampleGroupModel, ExampleGroup, replace_found)


def resolve_example_entry_include(found: FoundItem[IncludeExample]) -> bool:
    """Load example entries include and splice into list."""
    return expand_splice(found, gate_include_example_entries_input, IncludeExampleEntriesModel, ExampleEntry)


def resolve_guardrails_constraints_include(found: FoundItem[IncludeGuardrailsConstraints]) -> bool:
    """Load guardrails constraints and set inline field."""
    return expand_field(
        found, gate_include_guardrails_constraints_input,
        IncludeConstraintsModel, GuardrailsConstraints,
        "guardrails_constraints", "include_guardrails_constraints",
    )


def resolve_guardrails_anti_patterns_include(found: FoundItem[IncludeGuardrailsAntiPatterns]) -> bool:
    """Load guardrails anti-patterns and set inline field."""
    return expand_field(
        found, gate_include_guardrails_anti_patterns_input,
        IncludeAntiPatternsModel, GuardrailsAntiPatterns,
        "guardrails_anti_patterns", "include_guardrails_anti_patterns",
    )


def resolve_success_criteria_include(found: FoundItem[IncludeSuccessCriteria]) -> bool:
    """Load success criteria include and splice into list."""
    return expand_splice(found, gate_include_success_criteria_input, IncludeSuccessModel, SuccessItem)


def resolve_failure_criteria_include(found: FoundItem[IncludeFailureCriteria]) -> bool:
    """Load failure criteria include and splice into list."""
    return expand_splice(found, gate_include_failure_criteria_input, IncludeFailureModel, FailureItem)
