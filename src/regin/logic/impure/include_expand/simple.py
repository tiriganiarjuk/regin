"""Include expand simple functions — three structural expansion strategies.

CC=1-3. Import from gates/primitive and tree_mutate/primitive.

Gate-validated include expansion implementing the three strategies for
injecting external file content into the agent definition model tree.
Each function loads an external file through a validation gate, bridges
the loaded data into the host model's type system, and mutates the model
tree in place.

The three strategies match the three structural relationships between
include references and their host containers:
  splice:  1:many into a list (one include -> N items)
  replace: 1:1 substitution (one include -> one value)
  field:   set inline field + clear include reference
"""

from pathlib import Path
from typing import Callable

from pydantic import BaseModel, RootModel

from regin.logic.impure.gates.primitive import NornirGate, call_input_gate
from regin.logic.impure.tree_mutate.primitive import splice_found
from regin.structure.model.found_item import FoundItem


def expand_splice(
    found: FoundItem,
    gate: NornirGate,
    fragment_cls: type[RootModel],
    target_cls: type[BaseModel],
) -> bool:
    """1:many expansion into a list — one include reference becomes N items.

    The include reference occupies one slot in a list; the loaded content
    contains multiple items. After expansion, the single include reference
    is replaced by the loaded items in-place. The bridge step
    (model_validate_json through fragment_cls then target_cls) ensures the
    loaded data conforms to the host schema, not just the fragment schema.

    Used for: instructions, example entries, success criteria, failure criteria.
    """
    result = call_input_gate(gate, Path(found.value.include.root))
    if not result.ok:
        raise ValueError(f"Gate '{gate.__name__}' failed: {result.error}")
    loaded = fragment_cls.model_validate_json(result.data)
    host_items = [target_cls.model_validate_json(item.model_dump_json()) for item in loaded.items.root]
    return splice_found(found, host_items)


def expand_replace(
    found: FoundItem,
    gate: NornirGate,
    fragment_cls: type[RootModel],
    target_cls: type[BaseModel],
    replace_fn: Callable[[FoundItem, BaseModel], bool],
) -> bool:
    """1:1 substitution — one include reference replaced by one loaded value.

    Used for: example groups, where one IncludeExampleGroup reference is
    replaced by one ExampleGroup. The replace_fn callback is injected to
    avoid importing tree_mutate at the composed level (maintaining the CC
    import boundary).
    """
    result = call_input_gate(gate, Path(found.value.include.root))
    if not result.ok:
        raise ValueError(f"Gate '{gate.__name__}' failed: {result.error}")
    loaded = fragment_cls.model_validate_json(result.data)
    host_value = target_cls.model_validate_json(loaded.model_dump_json())
    return replace_fn(found, host_value)


def expand_field(
    found: FoundItem,
    gate: NornirGate,
    fragment_cls: type[RootModel],
    target_cls: type[BaseModel],
    inline_field: str,
    include_field: str,
) -> bool:
    """Field-level injection — set inline field and clear include reference.

    Instead of replacing the include reference itself, this strategy sets an
    inline field on the parent model and clears the include field. After
    expansion, the include field becomes None and the inline field contains
    the loaded data.

    Used for: guardrails constraints and anti-patterns, where the include is
    a sibling field to the inline content field.
    """
    result = call_input_gate(gate, Path(found.value.include.root))
    if not result.ok:
        raise ValueError(f"Gate '{gate.__name__}' failed: {result.error}")
    loaded = fragment_cls.model_validate_json(result.data)
    host_data = target_cls.model_validate_json(loaded.items.model_dump_json())
    setattr(found.parent, inline_field, host_data)
    setattr(found.parent, include_field, None)
    return True
