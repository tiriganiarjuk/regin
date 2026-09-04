# PLAN — Regin Branch Build (Levels 1-5)

## Scope

Build 9 branches covering levels 1-5 of the DAG content pipeline.
Deferred: level3_permissions_resolve, level6_universal_merge, level7_render_regroup, level8_anthropic_resolve.

## Test Cases

Two end-to-end agent definitions chain through the entire DAG:
- `definitions/agents/agent-rebuilder-opus.toml` (+ 5 includes in `definitions/prompts/agent-rebuilder/`)
- `definitions/agents/truth-system-quality-control.toml` (+ 5 includes in `definitions/prompts/truth-system-quality-control/`)

**Validation strategy:** Run each branch against both definitions. The output gate validates the checkpoint TOML. That checkpoint becomes input for the next branch. If the delta is wrong, the next gate rejects it. The chain is self-validating.

---

## CONTEXT REMINDER — Read Before Every Phase

> **Gates handle ALL IO.** Python never reads or writes files. If you find `Path.read_text()` or `open()`, STOP.
> **Steps are named by level**, not sequentially. Same level = parallel. `level{N}_{branch}_{operation}.py`.
> **Gates are named by checkpoint**, not branch. `gate_{checkpoint}_{direction}`.
> **The work function is the delta** between input and output schema. Nothing more.
> **Frozen Pydantic models everywhere.** Use `model_copy(update={})` for transforms. `model_dump_json(by_alias=True, exclude_none=True)` once per branch.
> **NO TYPE SHEDDING.** Typed Pydantic models all the way. Never `dict`, never `dict[str, Any]`, never `.model_dump()` to work with dicts. Dicts seem simpler but make everything messy — you lose validation, autocomplete, frozen guarantees, and the ability to reason about the data shape. Parse to a model at the gate boundary, transform as models, serialize once at the end.
> **Import path IS the safety contract.** `functions.pure` = no side effects. `functions.impure` = has IO.
> **Each function does ONE thing.** If gleipnir flags it, find the functional primitive. Don't suppress.
>
> Architecture docs: `DAG_EXPLAINED.md` (shape), `BRANCH_EXPLAINED.md` (pattern), `CLAUDE.md` (anti-patterns)

---

## GUARDRAIL MANDATE

```
uv run pytest tests/test_guardrails.py
```

Run after EVERY file. Not after a phase. After every file. Full output — no `-k` filters, no `| tail`, no `--tb=short`. Gleipnir output tells you WHAT is wrong AND how to fix it. Architectural debt compounds silently — if you defer guardrail fixes, you will reach a point where refactoring out of it costs more than starting over.

**Gleipnir thresholds (from `.gleipnir/rules.toml`):**
- max_function_lines = 50
- max_function_params = 5
- max_nesting_depth = 4
- max_quarantine_per_tool = 4

---

## Phase 0: Infrastructure

Create the package skeleton and shared modules before any branches.

### 0a. Package `__init__.py` files

Create empty `__init__.py` in:
- `src/regin/__init__.py`
- `src/regin/branches/__init__.py`
- `src/regin/functions/__init__.py`
- `src/regin/functions/pure/__init__.py`
- `src/regin/functions/impure/__init__.py`
- `src/regin/structures/__init__.py`

### 0b. `structures/gate_types.py` — Typed gate result

The Nornir gate API returns `{"ok": bool, "data": json_string, "error": {...}}`.
Create a frozen Pydantic model wrapping this. Keep it minimal — just the shape.

### 0c. `functions/impure/gates.py` — Gate loading boundary

The ONE impure boundary for gate IO. Loads compiled `.so` gate modules from `~/ai/tools/lib/`.
Three functions:
- `load_gate(name: str) -> module` — importlib.util loads the `.so`, caches in dict
- `call_input_gate(gate_name: str, file_path: Path) -> str` — calls `gate.validate(str(path))`, returns JSON string or raises
- `call_output_gate(gate_name: str, json_data: str, file_path: Path) -> str` — calls `gate.validate(json_data, str(path))`, returns JSON string or raises

> **FP REFERENCE:** This is the IO externalization boundary. Everything outside this module is pure.
> `functions.impure.gates` — the import path tells you: this has side effects, this touches the filesystem.
> Every branch imports from here. No branch ever touches IO directly.

### 0d. Run guardrails. Fix everything.

---

## Phase 1: Level 1 — `branches/level1_paths_resolve.py`

### Delta
- **Input:** `gate_raw_definition_input` → raw definition JSON
- **Output:** `gate_paths_resolved_output` ← paths-resolved JSON
- **Transform:** Prepend workspace root to all workspace-relative paths. Type narrowing: `UnionPathAny` → `PathAbsolute`, `UnionPathExistsAny` → `PathExistsAbsolute`. Remove relative-only path types.

### Pure function: `functions/pure/paths_resolve.py`
- Takes a raw definition Pydantic model + workspace root string
- Returns a paths-resolved Pydantic model
- Walks all path fields recursively and prepends workspace root to relative paths
- Must handle: `security.security_paths`, `security.context`, include paths in `execution` and `criteria`, `security.security_schema`, `security.security_io`

### Branch file
- Imports: `call_input_gate`, `call_output_gate` from `functions.impure.gates`
- Imports: pure transform from `functions.pure.paths_resolve`
- Imports: Pydantic models from `structures.raw_definition`, `structures.paths_resolved`
- Work function: parse JSON → call pure transform → serialize
- Entry function takes `input_path`, `output_path`, `workspace_root`

### Validate
- Run against both test cases
- Output gate must accept the result
- Output TOML written to `definitions/agents/{name}/paths_resolved.toml`

> **CONTEXT REMINDER:** The L1 delta is path absolutization. Raw definition has `UnionPathAny` (relative OR absolute). Paths-resolved has only `PathAbsolute`. The transform prepends workspace root to relative paths and passes absolute paths through unchanged.

### Run guardrails. Fix everything.

---

## Phase 2: Level 2 — `branches/level2_paths_verify.py`

### Delta
- **Gate:** `gate_paths_verified` (passthrough — no Python transform)
- **Transform:** NONE. The gate reads TOML, verifies all absolute paths exist on disk, writes TOML.

### Branch file
- Minimal: call the passthrough gate with input path and output path
- No work function. No pure functions. The gate IS the branch.

### Validate
- Run against both test cases
- Gate verifies all paths exist, writes `paths_verified.toml`
- If paths don't exist, gate returns `ok: false` with error details

### Run guardrails. Fix everything.

---

## Phase 3: Level 3 Content Reducers (4 parallel branches)

> **CONTEXT REMINDER:** All four reducers read the SAME input (paths_verified via `gate_paths_verified_input`) and each transforms a different section. The pattern is identical: find include references, read the include file via include gate, replace the reference with inline content. Extract the shared pattern FIRST, then build each reducer as a thin specialization.

### 3a. Shared pure function: `functions/pure/include_resolve.py`

The four L3 reducers share the same core operation: replace include references with inline content from include gates. Extract the shared logic:

- `resolve_instruction_includes(items, gate_caller)` — for each `IncludeInstruction` in the list, call the include gate on the path, parse the returned items, splice them into the list replacing the include reference
- `resolve_example_includes(groups, gate_caller)` — two levels: group-level includes (`IncludeExampleGroup`) and entry-level includes within groups
- `resolve_guardrail_includes(guardrails_model, gate_caller)` — resolve `include_guardrails_constraints` and `include_guardrails_anti_patterns` fields, merge items arrays
- `resolve_criteria_includes(criteria_list, gate_caller)` — for each `IncludeSuccessCriteria`/`IncludeFailureCriteria`, call include gate, splice items

> **FP REFERENCE:** These are impure at the boundary (they call include gates to read files) but the data transformation logic inside is pure. The gate_caller is injected — making the transform testable with fake callers. This is the sandwich pattern: impure shell, pure core.
>
> **IMPORTANT:** Include gates are INPUT gates — they read TOML files. Call them with `call_input_gate("gate_include_{type}_input", include_path)`. They return JSON with `{items: [...]}` (or unwrapped object for example-group).

### 3b. `branches/level3_content_instructions_reduce.py`

**Delta:**
- `execution.execution_instructions`: `list[InstructionStep | IncludeInstruction]` → `list[InstructionStep]`
- Include gate: `gate_include_execution_instructions_input` returns `{items: [InstructionStep, ...]}`
- All other sections pass through unchanged

**Work function:** Parse paths_verified JSON → resolve instruction includes → serialize as instructions_reduced JSON

### 3c. `branches/level3_content_examples_reduce.py`

**Delta:**
- `execution.execution_examples`: `list[ExampleGroup | IncludeExampleGroup]` → `list[ExampleGroup]`
- Two levels of include resolution:
  1. Group level: `IncludeExampleGroup` → call `gate_include_example_group_input` → returns `ExampleGroup` directly (unwrapped)
  2. Entry level within groups: if `example_entries` contains includes → call `gate_include_example_entries_input` → returns `{items: [ExampleEntry, ...]}`
- All other sections pass through unchanged

### 3d. `branches/level3_content_guardrails_reduce.py`

**Delta:**
- `criteria.guardrails.include_guardrails_constraints` field REMOVED; content merged into `guardrails_constraints`
- `criteria.guardrails.include_guardrails_anti_patterns` field REMOVED; content merged into `guardrails_anti_patterns`
- Include gates: `gate_include_guardrails_constraints_input`, `gate_include_guardrails_anti_patterns_input` — both return `{items: [string, ...]}`
- All other sections pass through unchanged

### 3e. `branches/level3_content_success_reduce.py`

**Delta:**
- `criteria.success_criteria`: `list[SuccessItem | IncludeSuccessCriteria]` → `list[SuccessItem]`
- `criteria.failure_criteria`: `list[FailureItem | IncludeFailureCriteria]` → `list[FailureItem]`
- Include gates: `gate_include_success_criteria_input`, `gate_include_failure_criteria_input` — return `{items: [SuccessItem/FailureItem, ...]}`
- All other sections pass through unchanged

### Run guardrails after EACH branch file. Fix everything.

---

## Phase 4: Level 4 Content Merges (2 branches)

> **CONTEXT REMINDER:** Merge branches take TWO inputs and combine them. The critical invariant: shared sections (indirect, task, security) MUST be identical between the two inputs. If they diverge during parallel reduction, the merge MUST detect and fail. This is a safety check — it catches bugs in L3 reducers that accidentally modified sections they shouldn't have touched.

### 4a. Shared pure function: `functions/pure/section_compare.py`

Verifies that named sections are identical between two Pydantic models. Used by all three merge branches (L4 execution, L4 criteria, L5 includes).

- `verify_sections_match(model_a, model_b, section_names: list[str])` — compares JSON serialization of named sections. Raises on mismatch with diff details.

### 4b. `branches/level4_content_execution_merge.py`

**Delta:**
- **Input A:** `gate_instructions_reduced_input` → instructions-reduced JSON
- **Input B:** `gate_examples_reduced_input` → examples-reduced JSON
- **Output:** `gate_execution_merged_output` ← execution-merged JSON
- **Transform:** Verify `indirect`, `task`, `security`, `criteria` are identical between A and B. Take `execution` that has both reduced instructions AND reduced examples. (Since A has reduced instructions but unreduced examples, and B has reduced examples but unreduced instructions — the merge takes instructions from A and examples from B.)

### 4c. `branches/level4_content_criteria_merge.py`

**Delta:**
- **Input A:** `gate_guardrails_reduced_input` → guardrails-reduced JSON
- **Input B:** `gate_success_reduced_input` → success-reduced JSON
- **Output:** `gate_criteria_merged_output` ← criteria-merged JSON
- **Transform:** Verify `indirect`, `task`, `security`, `execution` are identical. Take `criteria` that has both reduced guardrails AND reduced success/failure. (A has reduced guardrails, B has reduced success/failure — merge takes guardrails from A and success/failure from B.)

### Run guardrails after EACH branch file. Fix everything.

---

## Phase 5: Level 5 — `branches/level5_content_includes_merge.py`

### Delta
- **Input A:** `gate_execution_merged_input` → execution-merged JSON
- **Input B:** `gate_criteria_merged_input` → criteria-merged JSON
- **Output:** `gate_includes_merged_output` ← includes-merged JSON
- **Transform:** Verify `indirect`, `task`, `security` are identical. Take `execution` from A (has both reduced instructions + examples), take `criteria` from B (has both reduced guardrails + success/failure).

> **CONTEXT REMINDER:** After L5, the content branch is complete. All includes are resolved to inline content. The definition has the same 5 sections (indirect, task, security, execution, criteria) but every include reference has been replaced with actual content. This is Red 4 — the last content-only checkpoint before permissions convergence at L6.

### Reuses
- `section_compare.verify_sections_match` from Phase 4a
- Same merge pattern as L4 branches

### Run guardrails. Fix everything.

---

## Phase 6: End-to-End Validation

Run the full L1→L5 chain against both test cases:
1. L1: raw definition → paths_resolved.toml
2. L2: paths_resolved.toml → paths_verified.toml
3. L3: paths_verified.toml → instructions_reduced.toml, examples_reduced.toml, guardrails_reduced.toml, success_reduced.toml
4. L4: instructions_reduced + examples_reduced → execution_merged.toml; guardrails_reduced + success_reduced → criteria_merged.toml
5. L5: execution_merged + criteria_merged → includes_merged.toml

Every output gate validates its checkpoint. Every input gate at the next level validates its input. If the chain completes without gate errors, the implementation is correct.

### Final guardrails run. Full output. Zero failures required.

---

## File Inventory (What Gets Created)

### Infrastructure
- `src/regin/__init__.py`
- `src/regin/branches/__init__.py`
- `src/regin/functions/__init__.py`
- `src/regin/functions/pure/__init__.py`
- `src/regin/functions/impure/__init__.py`
- `src/regin/structures/__init__.py`
- `src/regin/structures/gate_types.py`
- `src/regin/functions/impure/gates.py`

### Pure Functions
- `src/regin/functions/pure/paths_resolve.py`
- `src/regin/functions/pure/include_resolve.py`
- `src/regin/functions/pure/section_compare.py`

### Branches
- `src/regin/branches/level1_paths_resolve.py`
- `src/regin/branches/level2_paths_verify.py`
- `src/regin/branches/level3_content_instructions_reduce.py`
- `src/regin/branches/level3_content_examples_reduce.py`
- `src/regin/branches/level3_content_guardrails_reduce.py`
- `src/regin/branches/level3_content_success_reduce.py`
- `src/regin/branches/level4_content_execution_merge.py`
- `src/regin/branches/level4_content_criteria_merge.py`
- `src/regin/branches/level5_content_includes_merge.py`

---

## FP Architecture Summary

```
functions/impure/gates.py     ← THE boundary. All IO lives here. Import path says "impure".
functions/pure/paths_resolve.py    ← Pydantic model in, Pydantic model out. No IO.
functions/pure/include_resolve.py  ← Gate caller injected. Testable with fakes.
functions/pure/section_compare.py  ← Two models in, exception or nothing out.
branches/level*_*.py               ← Thin wiring: gate_in → parse → pure transform → serialize → gate_out
structures/*.py                    ← Generated from JSON Schema. Frozen. Do NOT edit.
structures/gate_types.py           ← Hand-written. Gate result wrapper.
```

> **The test for correctness:** Can you trace the data flow from raw TOML to includes_merged TOML through the code? Every step: which gate reads, which pure function transforms, which gate writes? If you can draw this from the code alone, the architecture is clean. If you need to read comments to understand it, the naming is wrong.
