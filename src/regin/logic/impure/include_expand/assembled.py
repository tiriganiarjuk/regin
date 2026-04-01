"""Include expand assembled — concrete resolve callbacks for walk_find_replace.

CC=1-3. Each callback gate-loads, bridges to host types, and mutates the tree.
Imports from simple (within module), tree_mutate/primitive, and tree_mutate/simple.

Seven concrete include resolution callbacks passed to walk_find_replace in
the L3 content reducers. Each implements one of three mutation strategies:

  splice:  1:many into a list (instructions, example entries, criteria items)
  replace: 1:1 substitution (example groups)
  field:   set inline field + clear include reference (guardrails)
"""

import gate_include_example_entries_input
import gate_include_example_group_input
import gate_include_execution_instructions_input
import gate_include_failure_criteria_input
import gate_include_guardrails_anti_patterns_input
import gate_include_guardrails_constraints_input
import gate_include_success_criteria_input

from regin.logic.impure.include_expand.simple import gate_load_include
from regin.logic.impure.tree_mutate.primitive import splice_found
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
    data = gate_load_include(gate_include_execution_instructions_input, found)
    loaded = IncludeInstructionsModel.model_validate_json(data)
    host_items = [InstructionStep.model_validate_json(item.model_dump_json()) for item in loaded.items.root]
    return splice_found(found, host_items)


def resolve_example_group_include(found: FoundItem[IncludeExampleGroup]) -> bool:
    """Load example group include and replace 1:1."""
    data = gate_load_include(gate_include_example_group_input, found)
    loaded = IncludeExampleGroupModel.model_validate_json(data)
    host_value = ExampleGroup.model_validate_json(loaded.model_dump_json())
    return replace_found(found, host_value)


def resolve_example_entry_include(found: FoundItem[IncludeExample]) -> bool:
    """Load example entries include and splice into list."""
    data = gate_load_include(gate_include_example_entries_input, found)
    loaded = IncludeExampleEntriesModel.model_validate_json(data)
    host_items = [ExampleEntry.model_validate_json(item.model_dump_json()) for item in loaded.items.root]
    return splice_found(found, host_items)


def resolve_guardrails_constraints_include(found: FoundItem[IncludeGuardrailsConstraints]) -> bool:
    """Load guardrails constraints and set inline field."""
    data = gate_load_include(gate_include_guardrails_constraints_input, found)
    loaded = IncludeConstraintsModel.model_validate_json(data)
    host_data = GuardrailsConstraints.model_validate_json(loaded.items.model_dump_json())
    setattr(found.parent, "guardrails_constraints", host_data)
    setattr(found.parent, "include_guardrails_constraints", None)
    return True


def resolve_guardrails_anti_patterns_include(found: FoundItem[IncludeGuardrailsAntiPatterns]) -> bool:
    """Load guardrails anti-patterns and set inline field."""
    data = gate_load_include(gate_include_guardrails_anti_patterns_input, found)
    loaded = IncludeAntiPatternsModel.model_validate_json(data)
    host_data = GuardrailsAntiPatterns.model_validate_json(loaded.items.model_dump_json())
    setattr(found.parent, "guardrails_anti_patterns", host_data)
    setattr(found.parent, "include_guardrails_anti_patterns", None)
    return True


def resolve_success_criteria_include(found: FoundItem[IncludeSuccessCriteria]) -> bool:
    """Load success criteria include and splice into list."""
    data = gate_load_include(gate_include_success_criteria_input, found)
    loaded = IncludeSuccessModel.model_validate_json(data)
    host_items = [SuccessItem.model_validate_json(item.model_dump_json()) for item in loaded.items.root]
    return splice_found(found, host_items)


def resolve_failure_criteria_include(found: FoundItem[IncludeFailureCriteria]) -> bool:
    """Load failure criteria include and splice into list."""
    data = gate_load_include(gate_include_failure_criteria_input, found)
    loaded = IncludeFailureModel.model_validate_json(data)
    host_items = [FailureItem.model_validate_json(item.model_dump_json()) for item in loaded.items.root]
    return splice_found(found, host_items)
