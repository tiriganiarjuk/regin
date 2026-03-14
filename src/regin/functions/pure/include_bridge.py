"""Bridge include fragment models to paths_resolved target types.

Each function takes gate-validated JSON, parses through the fragment
model (perfect structural match), then JSON round-trips each item
into the paths_resolved type system. This is the typed channel
between two independently generated model hierarchies.

Pure — JSON parsing and serialization only, no IO.
"""

from regin.structures.fragment.example_entries import (
    ExampleEntries as FragmentEntries,
)
from regin.structures.fragment.example_group import (
    ExampleGroup as FragmentGroup,
)
from regin.structures.fragment.execution_instructions import (
    ExecutionInstructions as FragmentInstructions,
)
from regin.structures.fragment.failure_criteria import (
    FailureCriteria as FragmentFailure,
)
from regin.structures.fragment.guardrails_anti_patterns import (
    GuardrailsAntiPatterns as FragmentAntiPatterns,
)
from regin.structures.fragment.guardrails_constraints import (
    GuardrailsConstraints as FragmentConstraints,
)
from regin.structures.fragment.success_criteria import (
    SuccessCriteria as FragmentSuccess,
)
from regin.structures.schema.agent_paths_resolved import (
    ExampleEntry,
    ExampleGroup,
    FailureItem,
    GuardrailsAntiPattern,
    GuardrailsConstraint,
    InstructionStep,
    SuccessItem,
)


def bridge_instruction_steps(gate_json: str) -> list[InstructionStep]:
    """Bridge execution instruction items to target types."""
    fragment = FragmentInstructions.model_validate_json(gate_json)
    return [
        InstructionStep.model_validate_json(step.model_dump_json())
        for step in fragment.items.root
    ]


def bridge_example_group(gate_json: str) -> ExampleGroup:
    """Bridge a complete example group to target type."""
    fragment = FragmentGroup.model_validate_json(gate_json)
    return ExampleGroup.model_validate_json(fragment.model_dump_json())


def bridge_example_entries(gate_json: str) -> list[ExampleEntry]:
    """Bridge example entry items to target types."""
    fragment = FragmentEntries.model_validate_json(gate_json)
    return [
        ExampleEntry.model_validate_json(entry.model_dump_json())
        for entry in fragment.items.root
    ]


def bridge_guardrails_constraints(gate_json: str) -> list[GuardrailsConstraint]:
    """Bridge guardrails constraint items to target types."""
    fragment = FragmentConstraints.model_validate_json(gate_json)
    return [
        GuardrailsConstraint.model_validate_json(item.model_dump_json())
        for item in fragment.items.root
    ]


def bridge_guardrails_anti_patterns(gate_json: str) -> list[GuardrailsAntiPattern]:
    """Bridge guardrails anti-pattern items to target types."""
    fragment = FragmentAntiPatterns.model_validate_json(gate_json)
    return [
        GuardrailsAntiPattern.model_validate_json(item.model_dump_json())
        for item in fragment.items.root
    ]


def bridge_success_criteria(gate_json: str) -> list[SuccessItem]:
    """Bridge success criteria items to target types."""
    fragment = FragmentSuccess.model_validate_json(gate_json)
    return [
        SuccessItem.model_validate_json(item.model_dump_json())
        for item in fragment.items.root
    ]


def bridge_failure_criteria(gate_json: str) -> list[FailureItem]:
    """Bridge failure criteria items to target types."""
    fragment = FragmentFailure.model_validate_json(gate_json)
    return [
        FailureItem.model_validate_json(item.model_dump_json())
        for item in fragment.items.root
    ]
