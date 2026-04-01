# Regin — The Branch Pattern

## The Principle

Every branch in the DAG does exactly one thing: **transform the delta between its input checkpoint schema and its output checkpoint schema.**

```
                       checkpoint.toml
                             │
                 ┌───────────▼────────────┐
                 │ gate_checkpoint_input   │
                 │   (read + validate)    │
                 └───────────┬────────────┘
                             │ JSON
                             ▼
                         ┌───────┐
                         │ { Δ } │
                         └───┬───┘
                             │ JSON
                 ┌───────────▼────────────┐
                 │ gate_checkpoint_output  │
                 │  (validate + write)    │
                 └───────────┬────────────┘
                             │
                       checkpoint.toml
```

The input gate reads the file and validates. The output gate validates and writes the file. The Python in between is ONLY the delta — what changed between the two schemas.

## Checkpoints, Not Branches

Gates are named after the **schema they validate**, not the branch they belong to.

```
  {BRANCH A}
      │
      ▼
gate_X_output  ──▶  X.toml  ──▶  gate_X_input
                                      │
                                      ├──▶ {BRANCH B}
                                      ├──▶ {BRANCH C}
                                      └──▶ {BRANCH D}
```

The checkpoint file is the interface between branches. The output gate writes it, the input gate reads it. Any branch that needs schema X calls `gate_X_input` — it doesn't know or care who wrote the file.

This is why `gate_paths_verified_input` serves all five level-3 branches. One gate, one schema, many consumers. The gate is the checkpoint, not the branch.

## What the Gates Do

Gates are compiled Rust (PyO3) modules produced by Nornir. Each gate embeds a JSON Schema at compile time. Every gate handles IO directly:

**Input gate** (`gate_X_input`):
1. **Reads** the TOML checkpoint file from disk
2. **Validates** against its embedded schema
3. **Converts** TOML → JSON
4. **Returns** validated JSON to the branch

**Output gate** (`gate_X_output`):
1. **Receives** JSON from the branch
2. **Validates** against its embedded schema
3. **Converts** JSON → TOML
4. **Writes** the TOML checkpoint file to disk

**Passthrough gate** (`gate_paths_verified`):
1. **Reads** the TOML checkpoint file
2. **Validates** (including filesystem path existence checks)
3. **Writes** the validated TOML checkpoint file
4. Pass/fail only — no Python transform

Every checkpoint is TOML on disk. Every gate converts TOML ↔ JSON at the boundary. The Python between gates always works with JSON. The format on disk is always TOML. No exceptions.

Gates are the zero-trust IO boundary. No Python code reads files. No Python code writes files. No Python code validates structure. The gates do all of this. The Python code's only job is the delta.

## What the Delta Is

The delta is what the output schema requires that the input schema does not contain.

| Branch | Input schema says | Output schema says | Delta (the work) |
|--------|------------------|--------------------|-------------------|
| Paths Resolve | Paths are workspace-relative | Paths are absolute | Prepend workspace root |
| Paths Verify | Paths are absolute strings | Paths are verified-existing | Passthrough gate (filesystem check, no Python) |
| Instructions Reduce | Instructions may contain `{include: "path"}` | Instructions are all inline `{instruction_mode, instruction_text}` | Read include files, replace references with content |
| Examples Reduce | Examples may contain includes | Examples are all inline | Same pattern as instructions |
| Guardrails Reduce | Guardrails may contain includes | Guardrails are all inline string arrays | Same pattern |
| Success Reduce | Success/failure criteria may contain includes | Criteria are all inline `{definition, evidence}` | Same pattern |
| Permissions Resolve | Security section declares capabilities | Enforcement section contains calculated grants | 6-phase security resolution algorithm |
| Execution Merge | Two separate documents (instructions + examples) | One document with both | Verify shared sections match, combine |
| Criteria Merge | Two separate documents (guardrails + criteria) | One document with both | Verify shared sections match, combine |
| Includes Merge | Two separate documents (execution + criteria) | One document with all includes resolved | Verify shared sections match, combine |
| Universal Merge | Two branch documents (content + permissions) | One converged document | Verify shared sections match, add enforcement |
| Render Regroup | 6 domain-oriented sections | 12 consumption-oriented sections | Regroup fields by consumer need |
| Anthropic Resolve | Platform-agnostic render sections | Anthropic-specific tools, hooks, model, frontmatter | Apply vendor lookup tables |

## The Uniform Runner

Every branch follows the same harness:

```
gate_in(path)  →  { WORK }  →  gate_out(path)
```

The gate IS the IO boundary. No separate load. No separate write. The runner calls the input gate with a file path, gets JSON back, passes it to the work function, takes the JSON result, and passes it to the output gate with an output path.

```python
def run(input_gate, output_gate, work, input_path, output_path):
    json_in  = call_gate(input_gate, input_path)
    json_out = work(json_in)
    call_gate(output_gate, json_out, output_path)
```

For merge branches, multiple input gates:

```python
def run(input_gates, output_gate, work, input_paths, output_path):
    jsons    = [call_gate(g, p) for g, p in zip(input_gates, input_paths)]
    json_out = work(*jsons)
    call_gate(output_gate, json_out, output_path)
```

Same harness. Different arity.

## The Work Function Contract

Each branch provides a work function. The contract:

- **Receives:** JSON string(s) from input gate(s)
- **Returns:** JSON string for output gate
- **Inside:** Parses to Pydantic model(s), calls pure function(s), serializes result
- **Purity:** The work function itself may be impure (e.g., loading include files for the content reducers). The pure functions it calls are in `logic/pure/`. The work function is the composition point.

```python
def work(gated_json: str) -> str:
    """Transform the delta between input and output schema."""
    model = InputModel.model_validate_json(gated_json)

    result = transform(model)

    return result.model_dump_json(by_alias=True, exclude_none=True)
```

The serialization options are always the same: `by_alias=True` (match schema field names), `exclude_none=True` (omit absent optional fields). This happens once per branch, inside the work function, before the result is handed to the output gate.

## Why This Works

The gate pair defines the contract. The work function fulfills it. Nothing more.

- **If the delta is zero** (paths verify), there is no work function — the passthrough gate handles everything.
- **If the delta is structural** (merge branches), the work function combines documents and the output gate validates the combined result.
- **If the delta is computational** (permissions resolve), the work function runs an algorithm and the output gate validates the result.
- **If the delta is vendor-specific** (anthropic resolve), the work function applies lookup tables and the output gate validates the result.

The pattern never changes. The complexity lives in the pure functions the work function calls, not in the harness. The harness is infrastructure. The pure functions are the domain.

## Gate Inventory

Gates are named `gate_{checkpoint}_{direction}`. Every checkpoint schema gets an input/output pair. The passthrough gate is the sole exception.

| Checkpoint Schema | Input Gate | Output Gate |
|-------------------|-----------|-------------|
| `agent-raw-definition` | `gate_raw_definition_input` | — |
| `agent-paths-resolved` | — | `gate_paths_resolved_output` |
| `agent-paths-resolved` (verified) | `gate_paths_verified_input` | — |
| *(passthrough)* | `gate_paths_verified` | |
| `agent-instructions-reduced` | `gate_instructions_reduced_input` | `gate_instructions_reduced_output` |
| `agent-examples-reduced` | `gate_examples_reduced_input` | `gate_examples_reduced_output` |
| `agent-guardrails-reduced` | `gate_guardrails_reduced_input` | `gate_guardrails_reduced_output` |
| `agent-success-reduced` | `gate_success_reduced_input` | `gate_success_reduced_output` |
| `agent-execution-merged` | `gate_execution_merged_input` | `gate_execution_merged_output` |
| `agent-criteria-merged` | `gate_criteria_merged_input` | `gate_criteria_merged_output` |
| `agent-includes-merged` | `gate_includes_merged_input` | `gate_includes_merged_output` |
| `agent-permissions-resolved` | `gate_permissions_resolved_input` | `gate_permissions_resolved_output` |
| `agent-universal-format` | `gate_universal_format_input` | `gate_universal_format_output` |
| `agent-universal-render` | `gate_universal_render_input` | `gate_universal_render_output` |
| `agent-anthropic-render` | — | `gate_anthropic_render_output` |
