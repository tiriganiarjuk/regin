# PLAN — Regin

What is left. A finished item is removed from this list.

- **Move `datamodel-code-generator` to 0.91.0.** The conditions and the consequence for `logic/transform/codegen_clean/` are in the dev-group comment in `pyproject.toml`.
- **Name the imported symbols in the transform modules.** `section_regroup/` and `vendor_compose/` import the two generated render modules whole, as `render` and `anthr`; the read-time dependency report asks for `from <module> import <name>`. The two modules define many classes with the same name, so the form of the aliases has to be chosen first.
