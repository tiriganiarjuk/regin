# PLAN — Regin

What is left. A finished item is removed from this list.

- **Move `datamodel-code-generator` to 0.91.0.** The conditions and the consequence for `logic/transform/codegen_clean/` are in the dev-group comment in `pyproject.toml`.
- **Settle the module-import form.** The read-time dependency report lists `from <package> import <module>` imports — in `cli.py` and across the transform modules — as importing a name from an `__init__.py` that does not define it. Either the imports change to name the defining file, or the report learns that a submodule is a valid target. That is the user's call.
- **A missing schema should fail the model generator.** `generate_structures.py` prints `SKIP` for a schema it cannot find and still exits 0.
- **Fill in or remove `REFRESH.md`.** It is the workspace template with its document map and critical decisions unfilled.
