# ATTENTION — type the nornir tool result as two outcomes

From the Nornir workspace, 2026-11-16.

## What is wrong

Every nornir gate and reader returns exactly one of two outcomes: success, with `data` a string
and `error` None; or refusal, with `data` None and `error` present
(`~/ai/smidja/nornir/capability/tool_face_io/src/lib.rs`, `py_contract`).

`src/regin/structure/model/gate_types.py` types the result as `GateResult` with three
independent fields — `ok: bool`, `data: str | None = None`, `error: GateError | None = None` —
which accepts combinations the tools never return. `src/regin/logic/impure/registry/simple.py`
checks only `result.ok`, then passes `result.data` to `model_validate_json`, where the type still
allows `None`.

## What to do

1. Replace `GateResult` with one model per outcome, as `MUST_READ_BEFORE_BUILDING.md` § Calling
   one from Python now shows (`~/ai/smidja/nornir/`): a success model with `ok: Literal[True]`,
   a refusal model with `ok: Literal[False]`, joined by `Field(discriminator="ok")`.
2. Callers match on the outcome's type: a refusal carries `error.type` to branch on, a success
   carries `data` for `model_validate_json`.
3. A working form is in Galdr: `~/ai/smidja/galdr/src/galdr/structure/model/gate_types.py` and
   `~/ai/smidja/galdr/src/galdr/logic/impure/gate_validate/simple.py`.

Delete this file when the fix is in.
