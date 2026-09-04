<!-- ═══════════════════════════════════════════════════════════════════════ -->
<!-- DO NOT EDIT THE PRELUDE. Before editing ANY part of this file, read     -->
<!-- /Users/johnny/ai/CONTEXT_MANAGEMENT_SYSTEM.md — the KFM section        -->
<!-- defines what this file is for and why it is not linked from anywhere.   -->
<!--                                                                          -->
<!-- DO NOT LINK THIS FILE. Not from the CONTEXT_MAP, not from CLAUDE.md,    -->
<!-- not from the README. Its name is uninformative on purpose.              -->
<!--                                                                          -->
<!-- Entries are FAILURE SHAPE with concrete facts routed out. An entry that -->
<!-- names files and functions is a clock: it will outlive them and then     -->
<!-- assert something false to a reader who arrived here because something   -->
<!-- had already gone wrong.                                                  -->
<!-- ═══════════════════════════════════════════════════════════════════════ -->

# KFM — Regin

Known failure modes. Each entry records something that actually went wrong here, badly
enough or often enough to be worth writing down: a mistake that kept recurring, one that
was tedious to rediscover, or one that cost hours nobody wanted to spend twice.

**This file is deliberately not linked from anything.** Not the CONTEXT_MAP, not CLAUDE.md,
not the README. It has a name that tells you nothing on purpose. That is not tidiness — it
is the point:

> A list of failure modes read *before* you have a model of the project is not a warning,
> it is a set of suggestions. Naming a mistake supplies it. And a vivid catalogue of nine
> concrete failures shadows the orientation gate it sits above — a reader absorbs the
> stories, feels informed about the project, and skips the documents that would actually
> have oriented them.
>
> Read at the right moment — when something has already gone wrong, or when you are about
> to touch a part with a known history — the same entries are worth what they cost. The
> content is not the problem. The timing is.

The mechanism for *when* a reader gets sent here is undecided. Until it is decided, nothing
points here, and that is intentional rather than an oversight.

**If you have landed here anyway:** read it as history, not as instruction. Nothing below
is a description of the tree as it stands now — check anything concrete against the code
before acting on it.

**Maintenance:** an entry retires when its vector is gone. A trap guarding code that no
longer exists is worse than no trap, because it is the rigid layer asserting something
false. This has already happened once. Nothing automatic enforces it.

---

## Scrapped work — what these cost

Previous sessions in this project:

- Named steps sequentially (`step_01`, `step_02`...) on a DAG — hiding parallelism and teaching false dependencies
- Put IO (file reads/writes) inside Python code when gates handle all IO
- Used `dict[str, Any]` instead of frozen Pydantic models
- Built ad-hoc Python validation instead of using JSON Schema — a SESSION-TERMINATING violation
- Written monolithic functions that gleipnir flags for doing too many things
- Confused the content branch (levels 3-5) with the permissions branch (level 3) — they are independent until level 6
- Created separate `loaders.py` and `writers.py` when gates handle IO directly

None of them felt uncertain while doing it.

---

## You Will Get These Things Wrong

### Putting IO in Python Code
**Detection:** If you find `Path`, `open()`, `read_text()`, `write_text()` anywhere in Python...
**Why it's wrong:** Gates handle ALL IO. Input gates read files and return JSON. Output gates take JSON and write files. Python code between gates never touches the filesystem. The only exception is include file loading during content reduction (levels 3 content branch), which is the step's domain-specific work.
**Recovery:** Read BRANCH_EXPLAINED.md "What the Gates Do"

### Naming Steps Sequentially
**Detection:** If you find yourself writing `step_01`, `step_02`, or any sequential numbering...
**Why it's wrong:** Sequential numbering on a DAG is a lie. It teaches every future LLM that steps depend on each other linearly. Orchestration is organized by domain: `orchestrate/{domain}/orchestrate.py`. Domain names describe what the step does, not when it runs.
**Recovery:** Read DAG_EXPLAINED.md "File Naming Convention"

### Naming Gates After Branches
**Detection:** If you find yourself thinking "this is the instructions gate" or "this is the permissions gate"...
**Why it's wrong:** Gates are named after the checkpoint schema they validate, not the branch they belong to. `gate_paths_verified_input` serves five different branches. The gate doesn't know or care which branch calls it.
**Recovery:** Read BRANCH_EXPLAINED.md "Checkpoints, Not Branches"

### Using dict Instead of Frozen Pydantic Models
**Detection:** If you find `dict[str, Any]` or `.model_dump()` anywhere except inside a work function before handing JSON to the output gate...
**Why it's wrong:** Type safety is end-to-end. Models are frozen (`ConfigDict(frozen=True)`). Transformations use `model_copy(update={})`. Serialization via `model_dump_json(by_alias=True, exclude_none=True)` happens ONCE per branch, inside the work function.
**Recovery:** Look at any work function — it parses JSON to a model, transforms, serializes back.

### Writing Ad-Hoc Validation Instead of JSON Schema
**Detection:** If you find `if field not in record` or `isinstance(record[field], str)` checks...
**Why it's wrong:** SESSION-TERMINATING VIOLATION. Schema validation means a `.schema.json` file exists and the compiled gate validates against it. Always. No exceptions.
**Recovery:** Read `documentation/operations/STANDARD_OPERATING_PROCEDURES.md` § Schema Validation.

### Breaking the DAG Shape
**Detection:** If you pass data from a level 3 content step to the permissions step, or make level 4 depend on level 3 permissions output...
**Why it's wrong:** The content branch (levels 3-5) and the permissions branch (level 3) are independent until level 6 (convergence). Breaking this creates implicit coupling.
**Recovery:** Read DAG_EXPLAINED.md "The Levels"

### Exceeding Gleipnir Constraints Then Suppressing
**Detection:** If you add `# type: ignore`, expand quarantine lists, or think "this function needs to be longer"...
**Why it's wrong:** Gleipnir makes bad patterns expensive. If a function triggers a length violation, it does too many things. Find the functional primitive.
**Recovery:** Re-read `~/ai/phoenix/coding_reference/AI_BREAKTHROUGHS_HEMINGWAY_CODING.md`

### Modifying Generated Structure Files
**Detection:** If you edit files in `structure/gen/` that were generated by `generate_structures.py`...
**Why it's wrong:** Files in `structure/gen/schema/` and `structure/gen/fragment/` are generated from JSON Schemas. Manual edits will be silently overwritten. Hand-written files live in `structure/model/` and `structure/config/`.
**Recovery:** Change the Verdandi YAML source → run Draupnir → run `generate_structures.py`.

---
