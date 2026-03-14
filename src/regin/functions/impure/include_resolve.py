"""Replace functions for include resolution.

Each function is a callback for walk_find_replace: receives a FoundItem,
loads the include file via its gate, splices or replaces the result.

List-based includes (instructions, examples, success, failure) use
splice_found — one include may expand to multiple inline items.

Field-based includes (guardrails) load to the inline field and clear
the include field on the parent model.

Example groups are 1:1 replacement — one include file = one group.

Impure — each function calls an input gate to load a file.
"""

from pathlib import Path

from regin.functions.impure.gates import call_input_gate
from regin.functions.impure.model_mutate import replace_found, splice_found
from regin.structures.found_item import FoundItem
from regin.structures.fragment.example_entries import (
    ExampleEntries as IncludeExampleEntriesModel,
)
from regin.structures.fragment.example_group import (
    ExampleGroup as IncludeExampleGroupModel,
)
from regin.structures.fragment.execution_instructions import (
    ExecutionInstructions as IncludeInstructionsModel,
)
from regin.structures.fragment.failure_criteria import (
    FailureCriteria as IncludeFailureModel,
)
from regin.structures.fragment.guardrails_anti_patterns import (
    GuardrailsAntiPatterns as IncludeAntiPatternsModel,
)
from regin.structures.fragment.guardrails_constraints import (
    GuardrailsConstraints as IncludeConstraintsModel,
)
from regin.structures.fragment.success_criteria import (
    SuccessCriteria as IncludeSuccessModel,
)
from regin.structures.schema.agent_paths_resolved import (
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


# --- Instructions (splice) ---


def resolve_instruction_include(found: FoundItem[IncludeInstruction]) -> bool:
    """Load an instruction include file and splice its steps into the list."""
    path = Path(found.value.include.root)
    json_data = call_input_gate("gate_include_execution_instructions_input", path)
    loaded = IncludeInstructionsModel.model_validate_json(json_data)
    host_items = [InstructionStep.model_validate_json(step.model_dump_json()) for step in loaded.items.root]
    return splice_found(found, host_items)


# --- Examples (group: replace, entry: splice) ---


def resolve_example_group_include(found: FoundItem[IncludeExampleGroup]) -> bool:
    """Load an example group include file and replace the reference."""
    path = Path(found.value.include.root)
    json_data = call_input_gate("gate_include_example_group_input", path)
    loaded = IncludeExampleGroupModel.model_validate_json(json_data)
    host_group = ExampleGroup.model_validate_json(loaded.model_dump_json())
    return replace_found(found, host_group)


def resolve_example_entry_include(found: FoundItem[IncludeExample]) -> bool:
    """Load an example entries include file and splice into the entries list."""
    path = Path(found.value.include.root)
    json_data = call_input_gate("gate_include_example_entries_input", path)
    loaded = IncludeExampleEntriesModel.model_validate_json(json_data)
    host_items = [ExampleEntry.model_validate_json(entry.model_dump_json()) for entry in loaded.items.root]
    return splice_found(found, host_items)


# --- Guardrails (field-based: load to inline, clear include) ---


def resolve_guardrails_constraints_include(found: FoundItem[IncludeGuardrailsConstraints]) -> bool:
    """Load guardrails constraints and set the inline field."""
    path = Path(found.value.include.root)
    json_data = call_input_gate("gate_include_guardrails_constraints_input", path)
    loaded = IncludeConstraintsModel.model_validate_json(json_data)
    host_data = GuardrailsConstraints.model_validate_json(loaded.items.model_dump_json())
    found.parent.guardrails_constraints = host_data
    found.parent.include_guardrails_constraints = None
    return True


def resolve_guardrails_anti_patterns_include(found: FoundItem[IncludeGuardrailsAntiPatterns]) -> bool:
    """Load guardrails anti-patterns and set the inline field."""
    path = Path(found.value.include.root)
    json_data = call_input_gate("gate_include_guardrails_anti_patterns_input", path)
    loaded = IncludeAntiPatternsModel.model_validate_json(json_data)
    host_data = GuardrailsAntiPatterns.model_validate_json(loaded.items.model_dump_json())
    found.parent.guardrails_anti_patterns = host_data
    found.parent.include_guardrails_anti_patterns = None
    return True


# --- Success / Failure criteria (splice) ---


def resolve_success_criteria_include(found: FoundItem[IncludeSuccessCriteria]) -> bool:
    """Load success criteria include file and splice into the list."""
    path = Path(found.value.include.root)
    json_data = call_input_gate("gate_include_success_criteria_input", path)
    loaded = IncludeSuccessModel.model_validate_json(json_data)
    host_items = [SuccessItem.model_validate_json(item.model_dump_json()) for item in loaded.items.root]
    return splice_found(found, host_items)


def resolve_failure_criteria_include(found: FoundItem[IncludeFailureCriteria]) -> bool:
    """Load failure criteria include file and splice into the list."""
    path = Path(found.value.include.root)
    json_data = call_input_gate("gate_include_failure_criteria_input", path)
    loaded = IncludeFailureModel.model_validate_json(json_data)
    host_items = [FailureItem.model_validate_json(item.model_dump_json()) for item in loaded.items.root]
    return splice_found(found, host_items)
