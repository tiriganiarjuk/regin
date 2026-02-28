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

1. **Do NOT put file IO in Python code.** Gates handle ALL IO. If you write `Path.read_text()`, `open()`, or `write_text()` anywhere in `functions/pure/`, you are wrong.

2. **Do NOT name steps sequentially.** Never `step_01`, `step_02`. Steps are named `level{N}_{branch}_{operation}.py`. The level number encodes DAG depth.

3. **Do NOT name gates after branches.** Gates are named after their checkpoint schema: `gate_{checkpoint}_{direction}`. The gate serves any branch that needs that schema.

4. **Do NOT use `dict[str, Any]`.** Use frozen Pydantic models. Transformations use `model_copy(update={})`.

5. **Do NOT write ad-hoc validation.** JSON Schema is the only validation mechanism. Ad-hoc `if field not in record` checks are a session-terminating violation.

6. **Do NOT edit generated structure files.** Files in `structures/` that are listed in `generate_structures.py`'s `SCHEMA_MODULES` dict are generated from JSON Schemas. Edit the Verdandi YAML source, run Draupnir, then run `generate_structures.py`.

7. **Do NOT exceed Gleipnir constraints.** Max 50 lines per function, max 5 params, max 4 nesting depth. If you cannot fit, the function does too many things.

---

## Project Layout

```
tools/regin/
  pyproject.toml              # deps: loguru, markdown-it-py, pydantic
  generate_structures.py      # JSON Schema -> Pydantic models
  tool_registry.toml          # deployed Nornir writer tools
  CLAUDE.md                   # MANDATORY: read before writing any code
  DAG_EXPLAINED.md            # full DAG shape, level descriptions
  BRANCH_EXPLAINED.md         # gate IO model, runner harness, work contract
  CONTEXT_MAP.md              # where to find every piece of context
  src/regin/
    cli.py                    # entry point: regin command
    steps/                    # DAG runners (one file per pipeline node)
      level1_paths_resolve.py
      level2_paths_verify.py
      level3_content_*.py     # 4 parallel content reducers
      level3_permissions_resolve.py
      level4_content_*.py     # 2 content merges
      level5_content_includes_merge.py
      level6_universal_merge.py
      level7_render_regroup.py
      level8_anthropic_resolve.py
    functions/
      impure/
        gates.py              # loads + calls Nornir PyO3 gate .so modules
        runner.py             # uniform harness: gate_in -> work -> gate_out
        registry.py           # loads tool_registry.toml
      pure/                   # ALL domain logic (no IO)
        path_resolver.py      # workspace-relative -> absolute paths
        instructions.py       # reduce instruction includes
        examples.py           # reduce example includes
        guardrails.py         # reduce guardrail includes
        success_criteria.py   # reduce criteria includes
        mergers.py            # merge branch outputs (verify shared sections)
        permissions.py        # 6-phase security resolution (A-F)
        render.py             # 6 domain sections -> consumption sections
        anthropic_resolver.py # vendor-specific resolution (lookup tables)
        section_compare.py    # verify sections match during merges
        tool_discovery.py     # match agent spec against tool registry
    structures/               # Pydantic models
      [13 generated files]    # from JSON Schemas -- DO NOT EDIT
      gate_types.py           # GateResult, GateError (hand-written)
      errors.py               # 5 exception classes (hand-written)
      enums.py                # Capability, VendorTool, etc. (hand-written)
      vendor_lookup.py        # ANTHROPIC singleton lookup tables (hand-written)
      resolved_tool.py        # ResolvedTool, ToolBuildRequest (hand-written)
      resolved_grants.py      # OutputMode enum (hand-written)
      tool_registry.py        # ToolRegistryEntry model (hand-written)
  tests/
    test_guardrails.py        # Gleipnir architectural guardrails
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

This reads `schemas/agent-*.schema.json` and overwrites the generated Pydantic model files in `src/regin/structures/`. Hand-written files are not affected.

---

## Key Architecture Facts

- **Gates are compiled Rust (PyO3).** They embed JSON Schemas at compile time. They handle file IO, validation, and TOML/JSON conversion. Python never touches the filesystem (except include loading through include gates).

- **Every checkpoint on disk is TOML.** Gates convert TOML <-> JSON at the boundary. Python always works with JSON.

- **The runner harness is identical for every branch.** `gate_in(path) -> work(json) -> gate_out(json, path)`. Three variants: single, merge, passthrough.

- **Content branch and permissions branch are independent.** They diverge at level 3, converge at level 6. Do not pass data between them before convergence.

- **Level 8 fans out per vendor.** Currently only Anthropic. Each vendor resolver reads the same universal render (level 7 output) and applies vendor-specific lookup tables.
