"""Load include files through Nornir gates.

Each function calls the appropriate include gate, which reads TOML,
validates against the fragment schema, and returns JSON. The JSON
is parsed into the typed Pydantic model for that fragment type.

This is impure — gate calls read files from disk.
"""

from pathlib import Path

from regin.functions.impure.gates import call_input_gate
from regin.structures.fragment.example_entries import (
    ExampleEntries,
)
from regin.structures.fragment.example_group import (
    ExampleGroup,
)
from regin.structures.fragment.execution_instructions import (
    ExecutionInstructions,
)
from regin.structures.fragment.failure_criteria import (
    FailureCriteria,
)
from regin.structures.fragment.guardrails_anti_patterns import (
    GuardrailsAntiPatterns,
)
from regin.structures.fragment.guardrails_constraints import (
    GuardrailsConstraints,
)
from regin.structures.fragment.success_criteria import (
    SuccessCriteria,
)


def load_execution_instructions(path: str) -> ExecutionInstructions:
    """Load and validate an execution instructions include file."""
    json_data = call_input_gate("gate_include_execution_instructions_input", Path(path))
    return ExecutionInstructions.model_validate_json(json_data)


def load_example_group(path: str) -> ExampleGroup:
    """Load and validate an example group include file."""
    json_data = call_input_gate("gate_include_example_group_input", Path(path))
    return ExampleGroup.model_validate_json(json_data)


def load_example_entries(path: str) -> ExampleEntries:
    """Load and validate an example entries include file."""
    json_data = call_input_gate("gate_include_example_entries_input", Path(path))
    return ExampleEntries.model_validate_json(json_data)


def load_guardrails_constraints(path: str) -> GuardrailsConstraints:
    """Load and validate a guardrails constraints include file."""
    json_data = call_input_gate("gate_include_guardrails_constraints_input", Path(path))
    return GuardrailsConstraints.model_validate_json(json_data)


def load_guardrails_anti_patterns(path: str) -> GuardrailsAntiPatterns:
    """Load and validate a guardrails anti-patterns include file."""
    json_data = call_input_gate("gate_include_guardrails_anti_patterns_input", Path(path))
    return GuardrailsAntiPatterns.model_validate_json(json_data)


def load_success_criteria(path: str) -> SuccessCriteria:
    """Load and validate a success criteria include file."""
    json_data = call_input_gate("gate_include_success_criteria_input", Path(path))
    return SuccessCriteria.model_validate_json(json_data)


def load_failure_criteria(path: str) -> FailureCriteria:
    """Load and validate a failure criteria include file."""
    json_data = call_input_gate("gate_include_failure_criteria_input", Path(path))
    return FailureCriteria.model_validate_json(json_data)
