# Conditional Field Mappings

Each conditional field traced across all three schemas.
Shows the guarded field, its guard condition, and the actual field names at each stage.

Status key:
- `PRESENT` — conditional exists with correct field names
- `MISSING` — conditional should exist but does not
- `BROKEN` — conditional exists but references wrong field name
- `N/A` — field does not exist at this schema level
- `CONSUMED` — field was consumed by a transform and no longer exists

---

## 1. return_status

Guard: ONLY WHEN return_mode in [status, status-metrics]

| Schema | Guarded field | Guard field | Status |
|---|---|---|---|
| universal-format | `.task.return.return_status` | `.task.return.return_mode` | PRESENT |
| universal-render | `.return_format.status_instruction` | `.return_format.mode` | **MISSING** |
| anthropic-render | `.return_format.status_instruction` | `.return_format.mode` | **MISSING** |

## 2. return_metrics

Guard: ONLY WHEN return_mode in [status-metrics, metrics-output]

| Schema | Guarded field | Guard field | Status |
|---|---|---|---|
| universal-format | `.task.return.return_metrics` | `.task.return.return_mode` | PRESENT |
| universal-render | `.return_format.metrics_instruction` | `.return_format.mode` | **MISSING** |
| anthropic-render | `.return_format.metrics_instruction` | `.return_format.mode` | **MISSING** |

## 3. return_output

Guard: ONLY WHEN return_mode in [metrics-output, output]

| Schema | Guarded field | Guard field | Status |
|---|---|---|---|
| universal-format | `.task.return.return_output` | `.task.return.return_mode` | PRESENT |
| universal-render | `.return_format.output_instruction` | `.return_format.mode` | **MISSING** |
| anthropic-render | `.return_format.output_instruction` | `.return_format.mode` | **MISSING** |

## 4. output_file_name_template

Guard: ONLY WHEN output_file_name_known = partially

| Schema | Guarded field | Guard field | Status |
|---|---|---|---|
| universal-format | `.task.processing.output_file_name_template` | `.task.processing.output_file_name_known` | PRESENT |
| universal-render | `.output.name_template` | `.output.name_known` | **MISSING** |
| anthropic-render | `.output.name_template` | `.output.name_known` | **MISSING** |

## 5. output_file_name_instruction

Guard: ONLY WHEN output_file_name_known = unknown

| Schema | Guarded field | Guard field | Status |
|---|---|---|---|
| universal-format | `.task.processing.output_file_name_instruction` | `.task.processing.output_file_name_known` | PRESENT |
| universal-render | `.output.name_instruction` | `.output.name_known` | **MISSING** |
| anthropic-render | `.output.name_instruction` | `.output.name_known` | **MISSING** |

## 6. output_write_frequency

Guard: ONLY WHEN output_file_format = jsonl

| Schema | Guarded field | Guard field | Status |
|---|---|---|---|
| universal-format | `.task.processing.output_write_frequency` | `.task.processing.output_file_format` | PRESENT |
| universal-render | N/A | N/A | N/A (consumed at L3 → enforcement_output_tool) |
| anthropic-render | N/A | N/A | N/A (consumed at L3 → enforcement_output_tool) |

## 7. output_batch_size

Guard: ONLY WHEN output_write_frequency = batch

| Schema | Guarded field | Guard field | Status |
|---|---|---|---|
| universal-format | `.task.processing.output_batch_size` | `.task.processing.output_write_frequency` | PRESENT |
| universal-render | N/A | N/A | N/A (consumed at L3 → enforcement_output_tool) |
| anthropic-render | N/A | N/A | N/A (consumed at L3 → enforcement_output_tool) |

## 8. output_schema_embed

Guard: ONLY WHEN output_schema is present

| Schema | Guarded field | Guard field | Status |
|---|---|---|---|
| universal-format | `.security.security_schema.output_schema_embed` | `.security.security_schema.output_schema` | PRESENT |
| universal-render | `.output.schema_embed` | `.output.schema_path` | **MISSING** |
| anthropic-render | `.output.schema_embed` | `.output.schema_path` | **MISSING** |

## 9. output_tool_write_frequency

Guard: ONLY WHEN output_tool_format = jsonl

| Schema | Guarded field | Guard field | Status |
|---|---|---|---|
| universal-format | `.enforcement.enforcement_output_tool.output_tool_write_frequency` | `.enforcement.enforcement_output_tool.output_tool_format` | PRESENT |
| universal-render | `.writing_output.writing_output.output_tool_write_frequency` | `.writing_output.writing_output.output_tool_format` | PRESENT |
| anthropic-render | N/A | N/A | N/A (consumed by tool discovery) |

## 10. output_tool_batch_size

Guard: ONLY WHEN output_tool_write_frequency = batch

| Schema | Guarded field | Guard field | Status |
|---|---|---|---|
| universal-format | `.enforcement.enforcement_output_tool.output_tool_batch_size` | `.enforcement.enforcement_output_tool.output_tool_write_frequency` | PRESENT |
| universal-render | `.writing_output.writing_output.output_tool_batch_size` | `.writing_output.writing_output.output_tool_write_frequency` | PRESENT |
| anthropic-render | N/A | N/A | N/A (consumed by tool discovery) |

## 11. output_tool_schema_path

Guard: ONLY WHEN output_tool_format in [jsonl, json]

| Schema | Guarded field | Guard field | Status |
|---|---|---|---|
| universal-format | `.enforcement.enforcement_output_tool.output_tool_schema_path` | `.enforcement.enforcement_output_tool.output_tool_format` | **BROKEN** — if references `enforcement_output_tool_format` instead of `output_tool_format` |
| universal-render | `.writing_output.writing_output.output_tool_schema_path` | `.writing_output.writing_output.output_tool_format` | **BROKEN** — if references `enforcement_output_tool_format` instead of `output_tool_format` |
| anthropic-render | `.writing_output.schema_path` | N/A | **MISSING** — no conditional, and guard field (`output_tool_format`) was consumed |

## 12. dispatch_batch_size

Guard: ONLY WHEN dispatch_mode = batch

| Schema | Guarded field | Guard field | Status |
|---|---|---|---|
| universal-format | `.indirect.dispatch.dispatch_batch_size` | `.indirect.dispatch.dispatch_mode` | PRESENT |
| universal-render | `.dispatcher.batch_size` | `.dispatcher.dispatch_mode` | PRESENT |
| anthropic-render | `.dispatcher.batch_size` | `.dispatcher.dispatch_mode` | PRESENT |

---

## Summary

| # | Conditional | universal-format | universal-render | anthropic-render |
|---|---|---|---|---|
| 1 | return_status | PRESENT | **MISSING** | **MISSING** |
| 2 | return_metrics | PRESENT | **MISSING** | **MISSING** |
| 3 | return_output | PRESENT | **MISSING** | **MISSING** |
| 4 | output_file_name_template | PRESENT | **MISSING** | **MISSING** |
| 5 | output_file_name_instruction | PRESENT | **MISSING** | **MISSING** |
| 6 | output_write_frequency | PRESENT | N/A | N/A |
| 7 | output_batch_size | PRESENT | N/A | N/A |
| 8 | output_schema_embed | PRESENT | **MISSING** | **MISSING** |
| 9 | output_tool_write_frequency | PRESENT | PRESENT | N/A |
| 10 | output_tool_batch_size | PRESENT | PRESENT | N/A |
| 11 | output_tool_schema_path | **BROKEN** | **BROKEN** | **MISSING** |
| 12 | dispatch_batch_size | PRESENT | PRESENT | PRESENT |

**Totals:**
- universal-format: 11 PRESENT, 1 BROKEN
- universal-render: 3 PRESENT, 1 BROKEN, 5 MISSING, 3 N/A
- anthropic-render: 1 PRESENT, 1 MISSING, 6 N/A, 4 MISSING
