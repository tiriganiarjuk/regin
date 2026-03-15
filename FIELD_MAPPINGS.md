# Field Mappings: universal-format → universal-render → anthropic-render

Field-level trace across the L7 regroup and L8 anthropic resolve transforms.

Legend:
- `→` = renamed/relocated
- `⊕` = derived/computed (not a direct copy)
- `∅` = consumed (not in output)
- `PT` = pass-through (identical shape)

---

## Identity

| universal-format | universal-render | anthropic-render |
|---|---|---|
| .indirect.metadata.agent_name | ⊕ .identity.title (capitalized) | PT .identity.title |
| .indirect.metadata.agent_description | → .identity.description | PT .identity.description |
| .task.role.role_identity | → .identity.role_identity | PT .identity.role_identity |
| .task.role.role_responsibility | → .identity.role_responsibility | PT .identity.role_responsibility |
| .task.role.role_description | → .identity.role_description | PT .identity.role_description |
| .task.role.role_expertise[] | → .identity.role_expertise[] | PT .identity.role_expertise[] |
| .task.processing.capability_model | → .identity.capability_tier | ∅ consumed by model resolution |
| — | — | ⊕ .identity.model (from capability_tier lookup) |

## Security Boundary

| universal-format | universal-render | anthropic-render |
|---|---|---|
| .security.security_paths.paths_workspace | → .security_boundary.workspace_path | ∅ consumed → .critical_rules.workspace_path |
| .enforcement.enforcement_explicit_grants.read[] | → .security_boundary.capabilities.read[] | ∅ consumed → display + hooks |
| .enforcement.enforcement_explicit_grants.search[] | → .security_boundary.capabilities.search[] | ∅ consumed → display + hooks |
| .enforcement.enforcement_explicit_grants.inspect[] | → .security_boundary.capabilities.inspect[] | ∅ consumed → display + hooks |
| .enforcement.enforcement_explicit_grants.write[] | → .security_boundary.capabilities.write[] | ∅ consumed → display + hooks |
| .enforcement.enforcement_explicit_grants.edit[] | → .security_boundary.capabilities.edit[] | ∅ consumed → display + hooks |
| .enforcement.enforcement_explicit_grants.append[] | → .security_boundary.capabilities.append[] | ∅ consumed → display + hooks |
| — | — | ⊕ .security_boundary.display[].path (collapsed from capabilities) |
| — | — | ⊕ .security_boundary.display[].tools[] (grouped per path) |

## Implicit Grants

| universal-format | universal-render | anthropic-render |
|---|---|---|
| .enforcement.enforcement_implicit_grants.read[] | → .implicit_grants.capabilities.read[] | ∅ consumed → hooks |
| .enforcement.enforcement_implicit_grants.write[] | → .implicit_grants.capabilities.write[] | ∅ consumed → hooks |
| .enforcement.enforcement_implicit_grants.edit[] | → .implicit_grants.capabilities.edit[] | ∅ consumed → hooks |

## Input

| universal-format | universal-render | anthropic-render |
|---|---|---|
| .indirect.dispatch.dispatch_input_description | → .input.description | PT .input.description |
| .indirect.dispatch.dispatch_input_format | → .input.format | PT .input.format |
| .indirect.dispatch.dispatch_input_delivery | → .input.delivery | PT .input.delivery |
| .security.security_schema.input_schema | → .input.input_schema | PT .input.input_schema |
| .indirect.dispatch.dispatch_parameters[].param_name | → .input.parameters[].param_name | PT .input.parameters[].param_name |
| .indirect.dispatch.dispatch_parameters[].param_type | → .input.parameters[].param_type | PT .input.parameters[].param_type |
| .indirect.dispatch.dispatch_parameters[].param_required | → .input.parameters[].param_required | PT .input.parameters[].param_required |
| .indirect.dispatch.dispatch_parameters[].param_description | → .input.parameters[].param_description | PT .input.parameters[].param_description |
| .security.context.context_required[].context_label | → .input.context.context_required[].context_label | PT .input.context.context_required[].context_label |
| .security.context.context_required[].context_path | → .input.context.context_required[].context_path | PT .input.context.context_required[].context_path |
| .security.context.context_available[].context_label | → .input.context.context_available[].context_label | PT .input.context.context_available[].context_label |
| .security.context.context_available[].context_path | → .input.context.context_available[].context_path | PT .input.context.context_available[].context_path |

## Output

| universal-format | universal-render | anthropic-render |
|---|---|---|
| .task.processing.output_description | → .output.description | PT .output.description |
| .task.processing.output_file_format | → .output.format | PT .output.format |
| .task.processing.output_file_name_known | → .output.name_known | PT .output.name_known |
| .task.processing.output_file_name_template | → .output.name_template | PT .output.name_template |
| .task.processing.output_file_name_instruction | → .output.name_instruction | PT .output.name_instruction |
| .security.security_schema.output_schema | → .output.schema_path | PT .output.schema_path |
| .security.security_schema.output_schema_embed | → .output.schema_embed | PT .output.schema_embed |
| .security.security_io.io_output_file | → .output.output_file | PT .output.output_file |
| .security.security_io.io_output_directory | → .output.output_directory | PT .output.output_directory |

## Writing Output (Enforcement Tool)

| universal-format | universal-render | anthropic-render |
|---|---|---|
| .enforcement.enforcement_output_tool.output_tool_format | → .writing_output.writing_output.output_tool_format | ∅ consumed by tool discovery |
| .enforcement.enforcement_output_tool.output_tool_write_frequency | → .writing_output.writing_output.output_tool_write_frequency | ∅ consumed by tool discovery |
| .enforcement.enforcement_output_tool.output_tool_batch_size | → .writing_output.writing_output.output_tool_batch_size | → .writing_output.batch_size |
| .enforcement.enforcement_output_tool.output_tool_name_needed | → .writing_output.writing_output.output_tool_name_needed | → .writing_output.name_needed |
| .enforcement.enforcement_output_tool.output_tool_name_pattern | → .writing_output.writing_output.output_tool_name_pattern | → .writing_output.name_pattern |
| .enforcement.enforcement_output_tool.output_tool_schema_path | → .writing_output.writing_output.output_tool_schema_path | → .writing_output.schema_path |
| .enforcement.enforcement_output_tool.output_tool_file_path | → .writing_output.writing_output.output_tool_file_path | → .writing_output.file_path |
| .enforcement.enforcement_output_tool.output_tool_directory_path | → .writing_output.writing_output.output_tool_directory_path | → .writing_output.directory_path |
| — | — | ⊕ .writing_output.tool_name (from registry match) |
| — | — | ⊕ .writing_output.invocation_variant (derived from name_needed) |
| — | — | ⊕ .writing_output.invocation_display (composed heredoc) |

## Constraints

| universal-format | universal-render | anthropic-render |
|---|---|---|
| .criteria.guardrails.guardrails_constraints[] | → .constraints.rules[] | PT .constraints.rules[] |

## Anti-Patterns

| universal-format | universal-render | anthropic-render |
|---|---|---|
| .criteria.guardrails.guardrails_anti_patterns[] | → .anti_patterns.patterns[] | PT .anti_patterns.patterns[] |

## Return Format

| universal-format | universal-render | anthropic-render |
|---|---|---|
| .task.return.return_mode | → .return_format.mode | PT .return_format.mode |
| .task.return.return_status | → .return_format.status_instruction | PT .return_format.status_instruction |
| .task.return.return_metrics | → .return_format.metrics_instruction | PT .return_format.metrics_instruction |
| .task.return.return_output | → .return_format.output_instruction | PT .return_format.output_instruction |
| .security.security_schema.return_schema | → .return_format.return_schema | PT .return_format.return_schema |
| .criteria.success_criteria[].success_definition | → .return_format.success_criteria[].success_definition | PT .return_format.success_criteria[].success_definition |
| .criteria.success_criteria[].success_evidence[] | → .return_format.success_criteria[].success_evidence[] | PT .return_format.success_criteria[].success_evidence[] |
| .criteria.failure_criteria[].failure_definition | → .return_format.failure_criteria[].failure_definition | PT .return_format.failure_criteria[].failure_definition |
| .criteria.failure_criteria[].failure_evidence[] | → .return_format.failure_criteria[].failure_evidence[] | PT .return_format.failure_criteria[].failure_evidence[] |

## Dispatcher

| universal-format | universal-render | anthropic-render |
|---|---|---|
| .indirect.metadata.agent_name | → .dispatcher.agent_name | PT .dispatcher.agent_name |
| .indirect.metadata.agent_description | → .dispatcher.agent_description | PT .dispatcher.agent_description |
| .indirect.dispatch.dispatch_mode | → .dispatcher.dispatch_mode | PT .dispatcher.dispatch_mode |
| .indirect.dispatch.dispatch_background_mode | → .dispatcher.background_mode | PT .dispatcher.background_mode |
| .indirect.dispatch.dispatch_input_format | → .dispatcher.input_format | PT .dispatcher.input_format |
| .indirect.dispatch.dispatch_input_delivery | → .dispatcher.input_delivery | PT .dispatcher.input_delivery |
| .indirect.dispatch.dispatch_input_description | → .dispatcher.input_description | PT .dispatcher.input_description |
| .indirect.dispatch.dispatch_max_agents | → .dispatcher.max_agents | PT .dispatcher.max_agents |
| .indirect.dispatch.dispatch_batch_size[] | → .dispatcher.batch_size[] | PT .dispatcher.batch_size[] |
| .indirect.dispatch.dispatch_parameters[] | → .dispatcher.parameters[] | PT .dispatcher.parameters[] |
| .task.processing.output_file_format | → .dispatcher.output_format | PT .dispatcher.output_format |
| .task.processing.output_file_name_known | → .dispatcher.output_name_known | PT .dispatcher.output_name_known |
| .task.return.return_mode | → .dispatcher.return_mode | PT .dispatcher.return_mode |

## Instructions

| universal-format | universal-render | anthropic-render |
|---|---|---|
| .execution.execution_instructions[].instruction_mode | → .instructions.steps[].instruction_mode | PT .instructions.steps[].instruction_mode |
| .execution.execution_instructions[].instruction_text | → .instructions.steps[].instruction_text | PT .instructions.steps[].instruction_text |

## Examples

| universal-format | universal-render | anthropic-render |
|---|---|---|
| .execution.execution_examples[].example_group_name | → .examples.groups[].example_group_name | PT .examples.groups[].example_group_name |
| .execution.execution_examples[].example_display_headings | → .examples.groups[].example_display_headings | PT .examples.groups[].example_display_headings |
| .execution.execution_examples[].examples_max_number | → .examples.groups[].examples_max_number | PT .examples.groups[].examples_max_number |
| .execution.execution_examples[].example_entries[].example_heading | → .examples.groups[].example_entries[].example_heading | PT .examples.groups[].example_entries[].example_heading |
| .execution.execution_examples[].example_entries[].example_text | → .examples.groups[].example_entries[].example_text | PT .examples.groups[].example_entries[].example_text |

## Created at L8 (no upstream source)

| universal-format | universal-render | anthropic-render |
|---|---|---|
| — | — | ⊕ .frontmatter.name (from identity.title) |
| — | — | ⊕ .frontmatter.description (from identity.description) |
| — | — | ⊕ .frontmatter.model (from tier lookup) |
| — | — | ⊕ .frontmatter.permission_mode (const: bypassPermissions) |
| — | — | ⊕ .frontmatter.tools[] (from merged exploded grants) |
| — | — | ⊕ .frontmatter.hooks.output_tool (from resolved tool) |
| — | — | ⊕ .frontmatter.hooks.tool_entries[].tool (from exploded grants) |
| — | — | ⊕ .frontmatter.hooks.tool_entries[].paths[] (from exploded grants) |
| — | — | ⊕ .frontmatter.hooks.command_entries[].command (from exploded grants) |
| — | — | ⊕ .frontmatter.hooks.command_entries[].paths[] (from exploded grants) |
| — | — | ⊕ .critical_rules.workspace_path (from security_boundary) |
| — | — | ⊕ .critical_rules.has_output_tool (bool from tool discovery) |
| — | — | ⊕ .critical_rules.tool_name (from resolved tool) |
| — | — | ⊕ .critical_rules.name_needed (from enforcement fields) |
| — | — | ⊕ .critical_rules.batch_size (from enforcement fields) |

## Dead Fields (in universal-format, not carried to render)

| universal-format | Notes |
|---|---|
| .indirect.metadata.semantic_version | Not consumed by L7 or L8 |
| .security.security_capabilities.capabilities_requested[] | Consumed at L3 permissions, not carried to render |
| .security.security_capabilities.capabilities_prohibited[] | Consumed at L3 permissions, not carried to render |
| .security.security_io.io_input_directory | Not mapped to render output |
| .security.security_io.io_input_file | Not mapped to render output |
| .security.security_io.io_input_tempdir | Not mapped to render output |
| .security.security_io.io_scratch_tempdir | Not mapped to render output |
| .task.communication.notify[].notify_trigger | Not mapped to render output |
| .task.communication.notify[].notify_message | Not mapped to render output |
| .task.communication.notify[].notify_delivery | Not mapped to render output |
| .task.processing.scratch_needed | Not mapped to render output |
| .task.processing.output_write_frequency | Consumed at L3 permissions → enforcement tool |
| .task.processing.output_batch_size | Consumed at L3 permissions → enforcement tool |

## Conditional Fields

Fields guarded by `if/then/else` in the JSON Schema. These must NOT be emitted when the condition is unmet.

### In universal-format (inherited from earlier schemas)

| Field | Condition |
|---|---|
| .task.return.return_status | ONLY WHEN return_mode in [status, status-metrics] |
| .task.return.return_metrics | ONLY WHEN return_mode in [status-metrics, metrics-output] |
| .task.return.return_output | ONLY WHEN return_mode in [metrics-output, output] |
| .task.processing.output_file_name_template | ONLY WHEN output_file_name_known = partially |
| .task.processing.output_file_name_instruction | ONLY WHEN output_file_name_known = unknown |
| .task.processing.output_write_frequency | ONLY WHEN output_file_format = jsonl |
| .task.processing.output_batch_size | ONLY WHEN output_write_frequency = batch |

### In enforcement_output_tool (universal-format, universal-render, anthropic-render)

| Field | Condition |
|---|---|
| .*.output_tool_write_frequency | ONLY WHEN output_tool_format = jsonl |
| .*.output_tool_batch_size | ONLY WHEN output_tool_write_frequency = batch |
| .*.output_tool_schema_path | ONLY WHEN output_tool_format in [jsonl, json] |

### In dispatcher (universal-render, anthropic-render)

| Field | Condition |
|---|---|
| .dispatcher.batch_size | ONLY WHEN dispatch_mode = batch |
