# BRANCH PLAN — Level 8: Anthropic Resolve

## The Delta

Resolve platform-agnostic data into Anthropic/Claude Code-specific structures.

Input: `agent-universal-render` — 12 sections, platform-agnostic.
Output: `agent-anthropic-render` — 13 sections. 8 pass-through, 3 modified, 1 consumed, 2 created.

Gate in: `gate_universal_render_input` → JSON
Gate out: `gate_anthropic_render_output` → TOML

Authoritative design: `documentation/pipeline_render/ANTHROPIC_RENDER_DESIGN.md`

---

## The 8 Steps

### Step 1: Model Resolution (pure, independent)

`identity.capability_tier` → `identity.model` via TIER_TO_MODEL lookup.
The tier is consumed — replaced by resolved vendor model name.

### Step 2: Custom Tool Discovery (impure — reads tool_registry.toml)

Match `writing_output` enforcement spec against `tool_registry.toml`.
Returns: resolved tool name + invocation variant + invocation display (bash heredoc).
Returns None when: writing_output is null OR no match in registry.

**Impurity:** Loading the tool registry is IO. The registry loader (`functions/impure/registry.py`)
handles this. The matching logic is pure — receives registry entries as typed models.

### Step 3: Explode Grants (pure, independent)

Fan out capability-keyed grants to tool-keyed and command-keyed grants.
Runs on BOTH explicit and implicit grant sets independently.

```
{read: [/a, /b], search: [/a]} →
  tool_paths:    {Read: [/a, /b], Grep: [/a], Glob: [/a]}
  command_paths: {find: [/a]}
```

Paths merge within a tool (Read gets paths from `read` AND `inspect`)
but NOT across tools (Read and Grep keep separate path sets).

### Step 4: Security Boundary Display (pure, depends on 3)

Explicit exploded grants → display entries collapsed by workspace-relative path.
Strip workspace prefix from absolute paths. Group tools/commands per relative path.

```
tool_paths {Read: [/ws/truth/, /ws/schemas/], Grep: [/ws/truth/]}
workspace = /ws/
→ display: [{path: "./truth/", tools: [Read, Grep]}, {path: "./schemas/", tools: [Read]}]
```

Paths outside workspace remain absolute (e.g., `/tmp/bragi/`).

### Step 5: Build Hooks (pure, depends on 2 + 3)

Merge explicit + implicit exploded grants per tool. Assemble `HooksConfig` data structure.

**Schema note:** `HooksConfig` stores pure data — not rendered hook YAML.
Galdr (downstream template engine) renders this into CLI commands.

```
HooksConfig:
  output_tool: "append_truth_qc_report_record" | null
  tool_entries: [{tool: Read, paths: [/abs/...]}, {tool: Grep, paths: [...]}, ...] | null
  command_entries: [{command: find, paths: [/abs/...]}, ...] | null
```

Merge logic: for each tool, union the paths from explicit and implicit.

### Step 6: Compose Frontmatter (pure, depends on 1 + 3 + 5)

```
Frontmatter:
  name:            identity.title (AgentTitle)
  description:     identity.description
  model:           resolved model (from step 1)
  permission_mode: "bypassPermissions" (const)
  tools:           sorted unique tool names from merged exploded grants + Bash
  hooks:           HooksConfig (from step 5)
```

### Step 7: Create Critical Rules (pure, depends on 2)

```
CriticalRules:
  workspace_path:  from security_boundary.workspace_path
  has_output_tool: writing_output is not null AND custom_tool resolved
  tool_name:       custom_tool.tool_name | null
  name_needed:     writing_output.name_needed | null
  batch_size:      writing_output.batch_size | null
```

### Step 8: Populate Writing Output (pure, depends on 2)

Raw enforcement fields → resolved tool spec.

```
WritingOutputAnthropic:
  tool_name:          resolved name from registry match
  invocation_variant: "no-name" | "with-name" (derived from name_needed)
  invocation_display: composed bash heredoc (the ONE string L8 composes)
  name_needed:        from enforcement fields
  name_pattern:       from enforcement fields
  batch_size:         from enforcement fields
  schema_path:        from enforcement fields
  file_path:          from enforcement fields
  directory_path:     from enforcement fields
```

Null when: no custom tool resolved.

---

## Processing Order

```
Universal Render (12 sections)
  │
  ├──→ Step 1: Model resolution         (independent)
  ├──→ Step 2: Custom tool discovery     (independent, impure boundary)
  ├──→ Step 3: Explode grants            (independent)
  │      │
  │      ├──→ Step 4: Security display   (depends on 3)
  │      │
  │      └──→ Step 5: Build hooks        (depends on 2 + 3)
  │             │
  │             └──→ Step 6: Frontmatter  (depends on 1 + 3 + 5)
  │
  ├──→ Step 7: Critical rules            (depends on 2)
  ├──→ Step 8: Writing output            (depends on 2)
  │
  └──→ Pass-through: 8 sections unchanged
```

Sequential execution order: 1, 2, 3, 4, 5, 6, 7, 8.

---

## Lookup Tables

### TIER_TO_MODEL

```
fast-cheap         → haiku
standard           → sonnet
analytical         → sonnet
complex-reasoning  → opus
max-capability     → opus
inherit            → inherit
```

### CAPABILITY_TO_TOOLS

```
read    → [Read]
search  → [Grep, Glob]
inspect → [Read]
write   → [Write]
edit    → [Edit]
append  → [Edit]
```

Note: Read appears in both `read` and `inspect`. Paths merge within Read.

### CAPABILITY_TO_COMMANDS

```
search  → [find]
inspect → [ls, du, wc, stat, diff, tree]
```

---

## Intermediate Data

Grant explosion produces intermediate structures used by steps 4, 5, 6.
These are internal — not checkpoint schemas.

```
ExplodedGrants:
  tool_entries:    list[ToolPathEntry]     # [{tool: Read, paths: [/a, /b]}, ...]
  command_entries: list[CommandPathEntry]   # [{command: find, paths: [/a]}, ...]
```

Two instances: one for explicit grants, one for implicit grants.

Use the schema types (`ToolPathEntry`, `CommandPathEntry`) directly from
`agent_anthropic_render` to avoid creating intermediate structures.
Accumulate internally with `dict[str, set[str]]`, convert to typed list at return.

Custom tool discovery produces:

```
ResolvedTool:
  tool_name:          str
  invocation_variant: "no-name" | "with-name"
  invocation_display: str   # composed bash heredoc
```

Check if `structures/resolved_tool.py` already exists (CONTEXT_MAP lists it).

---

## Section Mapping

### Pass-through (8 sections — round-trip from universal_render types)

| L8 Section | L7 Source | Notes |
|------------|-----------|-------|
| input | input | identical schema shape |
| output | output | identical schema shape |
| instructions | instructions | identical schema shape |
| examples | examples | identical schema shape (nullable) |
| constraints | constraints | identical schema shape (nullable) |
| anti_patterns | anti_patterns | identical schema shape (nullable) |
| return_format | return_format | identical schema shape |
| dispatcher | dispatcher | identical schema shape |

### Modified (3 sections)

**identity → IdentityAnthropic:**
- `title`, `description`, `role_identity`, `role_responsibility`: pass through
- `capability_tier`: CONSUMED — replaced by `model: AnthropicModel`
- `role_description`, `role_expertise`: pass through (nullable)

**security_boundary → SecurityBoundaryAnthropic:**
- `workspace_path`: EXTRACTED to critical_rules
- `capabilities`: CONSUMED — exploded to display entries
- **Output:** `display: DisplayEntries | None` only
- **Note:** Section is NULLABLE in L8 (same as L7). Null when no explicit grants.

**writing_output → WritingOutputAnthropic:**
- Raw enforcement fields consumed by tool discovery
- **Output:** resolved tool spec (tool_name, invocation_variant, invocation_display + enforcement fields)
- Still nullable (null when no custom tool)

### Consumed (1 section — not in output)

**implicit_grants:** Merged with explicit grants during hook building (step 5).
Not carried forward — agent never sees implicit grants.

### Created (2 sections — not in input)

**critical_rules:** workspace_path + output tool summary fields.
**frontmatter:** name, description, model, permission_mode, tools, hooks.

---

## Architecture: Pure vs Impure

**Impure boundary:** Loading `tool_registry.toml` — handled by existing
`functions/impure/registry.py`. The registry entries arrive as typed models.

**Pure functions:** All 8 steps are pure once the registry is loaded.
The branch runner loads the registry, passes it to the pure resolver.

**The branch runner pattern:**
1. `call_input_gate("gate_universal_render_input", input_path)` → JSON
2. Load tool registry via `functions/impure/registry.py`
3. Call pure resolver: `resolve_anthropic(source, registry)` → AgentAnthropicRender
4. `model.model_dump_json(by_alias=True, exclude_none=True)` → JSON
5. `call_output_gate("gate_anthropic_render_output", json_out, output_path)`

---

## Pure Functions — File Structure

Grouped by what they DO:

### `anthropic_resolve_model.py` — Step 1

```
resolve_model(tier: AgentCapabilityTier) -> AnthropicModel
```

TIER_TO_MODEL lookup table lives here. One function.

### `anthropic_resolve_grants.py` — Step 3

```
explode_grants(capabilities: EnforcementExplicitGrants | EnforcementImplicitGrants)
    -> tuple[list[ToolPathEntry], list[CommandPathEntry]]
```

CAPABILITY_TO_TOOLS and CAPABILITY_TO_COMMANDS lookup tables live here.
Works on both explicit and implicit grants (same shape, different types —
use the inner capability fields).

### `anthropic_resolve_display.py` — Step 4

```
build_display(
    tool_entries: list[ToolPathEntry],
    command_entries: list[CommandPathEntry],
    workspace_path: str,
) -> DisplayEntries | None
```

Strips workspace prefix from paths. Groups tools/commands by relative path.
Returns None when no entries.

### `anthropic_resolve_tools.py` — Step 2

```
discover_tool(
    writing_output: WritingOutput | None,
    registry: list[ToolRegistryEntry],
) -> ResolvedTool | None
```

Matches enforcement spec against registry. Composes invocation_display heredoc.
Returns None when writing_output is null or no registry match.

### `anthropic_resolve_hooks.py` — Step 5

```
build_hooks(
    explicit_tools: list[ToolPathEntry],
    explicit_commands: list[CommandPathEntry],
    implicit_tools: list[ToolPathEntry],
    implicit_commands: list[CommandPathEntry],
    output_tool_name: str | None,
) -> HooksConfig
```

Merges explicit + implicit per tool (union paths). Assembles HooksConfig.

### `anthropic_resolve_sections.py` — Steps 6, 7, 8 + orchestrator

Composes the three output-only sections + assembles final AgentAnthropicRender:

```
build_frontmatter(identity, model, tools, hooks) -> Frontmatter
build_critical_rules(workspace_path, resolved_tool, writing_output) -> CriticalRules
build_writing_output(resolved_tool, enforcement_fields) -> WritingOutputAnthropic | None
resolve_anthropic(source, registry) -> AgentAnthropicRender
```

The orchestrator calls steps 1-8, passes through 8 sections, assembles the result.

---

## Invocation Display Composition

The ONE string L8 composes. Two variants:

**no-name** (fixed file path):
```
{tool_name} <<'EOF'
{json_data}
EOF
```

**with-name** (agent provides filename):
```
{tool_name} {name_placeholder} <<'EOF'
{json_data}
EOF
```

Where `name_placeholder` comes from the name_pattern template variable.

---

## Existing Infrastructure to Verify

Before building, check what already exists:

| File | CONTEXT_MAP Says | Status |
|------|------------------|--------|
| `functions/impure/registry.py` | Loads tool_registry.toml | Verify exists |
| `structures/resolved_tool.py` | ResolvedTool + ToolBuildRequest | Verify exists |
| `structures/tool_registry.py` | ToolRegistryEntry types | Verify exists |

If these exist, build on them. If not, create them.

---

## Type Conversion Strategy

**Pass-through sections:** Same round-trip pattern as L7 — `model_validate_json(section.model_dump_json(by_alias=True))`.

**Modified sections:** Construct directly from resolved data using target schema types.

**Lookup tables:** Defined as module-level dicts inside the pure function files.
Each maps a source enum value (string) to a target type.

---

## Context Reminders

- Authoritative design: `documentation/pipeline_render/ANTHROPIC_RENDER_DESIGN.md`
- `HooksConfig` stores PURE DATA — Galdr renders it into CLI commands. No string composition for hooks.
- `invocation_display` IS a composed string — the one string L8 creates.
- `implicit_grants` is CONSUMED — not in the output schema.
- `security_boundary` is NULLABLE in L8. Only field is `display: DisplayEntries | None`. Null when no explicit grants.
- Gates handle ALL IO. Python never reads files. Exception: registry loading is the impure boundary.
- The tool registry is NOT a checkpoint — it's configuration loaded by the impure layer.
- Run guardrails after every file.
