# QUICKSTART -- Regin Pipeline Resolver

## What It Does

Regin takes a raw agent definition TOML file and resolves it through 13 gated pipeline stages into a platform-ready render TOML. The pipeline is a DAG (not a linear sequence) with two branches that fan out at level 3 and converge at level 6, then fan out again at level 8 for vendor-specific resolution.

Input: `definitions/agents/<agent-name>.toml` (raw agent definition)
Output: `<agent-name>/anthropic_render.toml` (platform-ready render format)

Along the way, 12 intermediate TOML checkpoint files are written to the output directory.

---

## How to Run It

```bash
# From anywhere -- the tool is installed as a command
regin /path/to/agent-definition.toml

# With explicit output directory
regin /path/to/agent-definition.toml -o /path/to/output-dir

# Default output: sibling directory named after the input file stem
# e.g., agent-rebuilder.toml -> agent-rebuilder/
```

**Prerequisites:** Nornir gate `.so` modules must be compiled and present at `~/.ai/tools/lib/` (or override via `REGIN_GATE_LIB` env var). JSON Schema files must be current at `schemas/agent-*.schema.json`.

---

## What NOT to Do

Read `CLAUDE.md` in this directory before writing any code. It documents 7 specific failure modes that every LLM session has hit. The critical ones:

1. **Do NOT put file IO in Python code.** Gates handle ALL IO. If you write `Path.read_text()`, `open()`, or `write_text()` anywhere in `logic/pure/` or `logic/transform/`, you are wrong.

2. **Do NOT name steps sequentially.** Never `step_01`, `step_02`. Orchestration is organized by domain: `logic/orchestrate/{domain}/orchestrate.py`. Domain names describe what the step does, not when it runs.

3. **Do NOT name gates after branches.** Gates are named after their checkpoint schema: `gate_{checkpoint}_{direction}`. The gate serves any branch that needs that schema.

4. **Do NOT use `dict[str, Any]`.** Use frozen Pydantic models. Transformations use `model_copy(update={})`.

5. **Do NOT write ad-hoc validation.** JSON Schema is the only validation mechanism. Ad-hoc `if field not in record` checks are a session-terminating violation.

6. **Do NOT edit generated structure files.** Files in `structure/gen/` are generated from JSON Schemas by `generate_structures.py`. Edit the Verdandi YAML source, run Draupnir, then run `generate_structures.py`. Hand-written models live in `structure/model/` and `structure/config/`.

7. **Do NOT exceed Gleipnir constraints.** Each function does one thing. If gleipnir flags a violation, the function does too much — decompose, don't compress.

---

## Project Layout

```
tools/regin/
  pyproject.toml              # deps: loguru, markdown-it-py, pydantic
  generate_structures.py      # JSON Schema -> Pydantic models
  tool_registry.toml          # deployed Nornir writer tools
  CLAUDE.md                   # MANDATORY: read before writing any code
  BRANCH_EXPLAINED.md         # gate IO model, runner harness, work contract
  CONTEXT_MAP.md              # where to find every piece of context
  src/regin/
    cli.py                    # entry point: regin command
    logic/
      entry_point.py          # pipeline orchestration: trunk, fanout, convergence
      orchestrate/            # 9 domain directories (gate_in -> work -> gate_out)
        defaults_inject/      # L0: passthrough gate injects schema defaults
        paths_resolve/        # L1: resolve workspace-relative paths
        paths_verify/         # L2: passthrough gate verifies path existence
        content_reduce/       # L3: 4 parallel content reducers (run_instructions, etc.)
        permissions_resolve/  # L3: security -> enforcement grants
        content_merge/        # L4-L5: 3 merge steps (execution, criteria, includes)
        universal_merge/      # L6: converge content + permissions branches
        render_regroup/       # L7: 6 domain sections -> 12 consumption sections
        anthropic_resolve/    # L8: vendor-specific resolution
      impure/                 # IO boundary (gates, include loading, registry, tree mutation)
      pure/                   # computation (grant derivation, path ops, security validation, tree walk)
      transform/              # data reshaping (codegen cleanup, grant expand, paths, regroup, vendor)
    structure/
      gen/schema/             # 13 generated checkpoint models -- DO NOT EDIT
      gen/fragment/           # 7 generated include-fragment models -- DO NOT EDIT
      model/                  # hand-written domain models (gate_types, found_item, etc.)
      config/                 # hand-written config models (capability_tiers, tool_registry)
```

---

## Required Context for Development

| What you need to understand | Read this file |
|-----------------------------|----------------|
| Anti-patterns and failure modes | `tools/regin/CLAUDE.md` |
| Full DAG shape, which gates each step uses | `tools/regin/DAG_EXPLAINED.md` |
| How gates work, the runner harness, work function contract | `tools/regin/BRANCH_EXPLAINED.md` |
| Where every piece of knowledge lives | `tools/regin/CONTEXT_MAP.md` |
| Permission resolution algorithm (phases A-F) | `documentation/pipeline/SECURITY_RESOLUTION.md` |
| How Regin fits in the full tool chain | `definitions/TOOL_BUILDING.md` |
| Script standards, schema validation rules | `documentation/operations/STANDARD_OPERATING_PROCEDURES.md` |

---

## Running Guardrails

```bash
cd tools/regin && uv run pytest tests/test_guardrails.py
```

Run after every significant change. Not after finishing a phase -- after every file.

---

## Regenerating Structures After Schema Changes

```bash
cd tools/regin && ./generate_structures.py
```

This reads `schemas/agent-*.schema.json` and overwrites the generated Pydantic model files in `src/regin/structure/gen/`. Hand-written files in `structure/model/` and `structure/config/` are not affected.

---

## Key Architecture Facts

- **Gates are compiled Rust (PyO3).** They embed JSON Schemas at compile time. They handle file IO, validation, and TOML/JSON conversion. Python never touches the filesystem (except include loading through include gates).

- **Every checkpoint on disk is TOML.** Gates convert TOML <-> JSON at the boundary. Python always works with JSON.

- **The runner harness is identical for every branch.** `gate_in(path) -> work(json) -> gate_out(json, path)`. Three variants: single, merge, passthrough.

- **Content branch and permissions branch are independent.** They diverge at level 3, converge at level 6. Do not pass data between them before convergence.

- **Level 8 fans out per vendor.** Currently only Anthropic. Each vendor resolver reads the same universal render (level 7 output) and applies vendor-specific lookup tables.
