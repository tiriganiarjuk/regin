"""Include expand simple — gate-load content from include references.

CC=1-2. Import from gates/primitive only.

Single responsibility: call the gate for an include reference and return
the raw JSON data. Bridging to host types and tree mutation happen in the
assembled layer, which has visibility into both fragment models and
tree_mutate operations.
"""

from pathlib import Path

from regin.logic.impure.gates.primitive import NornirGate, call_input_gate, format_refusal
from regin.structure.model.found_item import FoundItem
from regin.structure.model.gate_types import GateRefusal


def gate_load_include(gate: NornirGate, found: FoundItem) -> str:
    """Gate-load content for an include reference. Returns raw JSON data.

    Calls the input gate with the include path from the found item.
    Raises ValueError on gate failure. The caller bridges the raw JSON
    to host types and applies the mutation strategy.
    """
    outcome = call_input_gate(gate, Path(found.value.include.root))
    if isinstance(outcome, GateRefusal):
        raise ValueError(format_refusal(gate.__name__, outcome))
    return outcome.data
