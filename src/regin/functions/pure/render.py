"""Regroup 6 domain-oriented sections into consumption-oriented sections.

Input: universal-format (indirect, task, security, execution, criteria, enforcement)
Output: universal-render (identity, security_boundary, implicit_grants, input,
        output, writing_output, constraints, anti_patterns, return_format,
        dispatcher, instructions, examples)

Works at JSON level. Helpers return JSON strings to avoid bare dict in signatures.
"""

import json

from regin.structures.universal_format import AgentUniversalFormat


def derive_title(agent_name: str) -> str:
    """Split agent name on hyphens and title-case each word."""
    return " ".join(word.capitalize() for word in agent_name.split("-"))


def build_identity(model: AgentUniversalFormat) -> str:
    """Build identity section JSON from indirect.metadata and task.role."""
    meta = model.indirect.metadata
    role = model.task.role
    processing = model.task.processing
    result = {
        "title": derive_title(meta.agent_name.root),
        "description": meta.agent_description.root,
        "role_identity": role.role_identity.root,
        "role_responsibility": role.role_responsibility.root,
        "capability_tier": processing.processing_capability_model.value,
    }
    if role.role_description is not None:
        result["role_description"] = role.role_description.root
    if role.role_expertise is not None:
        result["role_expertise"] = [item.root for item in role.role_expertise.root]
    return json.dumps(result)


def build_input_section(model: AgentUniversalFormat) -> str:
    """Build input section JSON from dispatch config and security."""
    dispatch = model.indirect.dispatch
    schema = model.security.security_schema
    security = model.security
    result = {
        "description": dispatch.dispatch_input_description.root,
        "format": dispatch.dispatch_input_format.value,
        "delivery": dispatch.dispatch_input_delivery.value,
    }
    if schema.security_input_schema is not None:
        result["input_schema"] = schema.security_input_schema.root
    if dispatch.dispatch_parameters is not None:
        result["parameters"] = json.loads(
            dispatch.dispatch_parameters.model_dump_json(by_alias=True, exclude_none=True),
        )
    if security.context is not None:
        result["context"] = json.loads(
            security.context.model_dump_json(by_alias=True, exclude_none=True),
        )
    return json.dumps(result)


def build_output_section(model: AgentUniversalFormat) -> str:
    """Build output section JSON from processing, schemas, and IO."""
    processing = model.task.processing
    schema = model.security.security_schema
    security_io = model.security.security_io
    result = {
        "description": processing.processing_output_description.root,
        "format": processing.processing_output_file_format.value,
        "name_known": processing.processing_output_file_name_known.value,
    }
    if schema.security_output_schema is not None:
        result["schema_path"] = schema.security_output_schema.root
    if schema.security_output_schema_embed is not None:
        result["schema_embed"] = schema.security_output_schema_embed.root
    if security_io.security_io_output_file is not None:
        result["output_file"] = security_io.security_io_output_file.root
    if security_io.security_io_output_directory is not None:
        result["output_directory"] = security_io.security_io_output_directory.root
    if processing.processing_output_file_name_template is not None:
        result["name_template"] = processing.processing_output_file_name_template.root
    if processing.processing_output_file_name_instruction is not None:
        result["name_instruction"] = processing.processing_output_file_name_instruction.root
    return json.dumps(result)


def build_return_format(model: AgentUniversalFormat) -> str:
    """Build return_format JSON from task.return and criteria."""
    ret = model.task.return_
    criteria = model.criteria
    result = {"mode": ret.return_mode.value}
    if ret.return_status is not None:
        result["status_instruction"] = ret.return_status.root
    if ret.return_metrics is not None:
        result["metrics_instruction"] = ret.return_metrics.root
    if ret.return_output is not None:
        result["output_instruction"] = ret.return_output.root
    if ret.return_schema is not None:
        result["return_schema"] = ret.return_schema.root
    if criteria.success_criteria is not None:
        result["success_criteria"] = json.loads(
            criteria.success_criteria.model_dump_json(by_alias=True, exclude_none=True),
        )
    if criteria.failure_criteria is not None:
        result["failure_criteria"] = json.loads(
            criteria.failure_criteria.model_dump_json(by_alias=True, exclude_none=True),
        )
    return json.dumps(result)


def build_dispatcher(model: AgentUniversalFormat) -> str:
    """Build dispatcher section JSON with everything a dispatcher needs."""
    meta = model.indirect.metadata
    dispatch = model.indirect.dispatch
    processing = model.task.processing
    result = {
        "agent_name": meta.agent_name.root,
        "agent_description": meta.agent_description.root,
        "dispatch_mode": dispatch.dispatch_mode.value,
        "background_mode": dispatch.dispatch_background_mode.value,
        "input_format": dispatch.dispatch_input_format.value,
        "input_delivery": dispatch.dispatch_input_delivery.value,
        "input_description": dispatch.dispatch_input_description.root,
        "output_format": processing.processing_output_file_format.value,
        "output_name_known": processing.processing_output_file_name_known.value,
        "return_mode": model.task.return_.return_mode.value,
    }
    if dispatch.dispatch_max_agents is not None:
        result["max_agents"] = dispatch.dispatch_max_agents.root
    if dispatch.dispatch_batch_size is not None:
        result["batch_size"] = json.loads(
            dispatch.dispatch_batch_size.model_dump_json(by_alias=True, exclude_none=True),
        )
    if dispatch.dispatch_parameters is not None:
        result["parameters"] = json.loads(
            dispatch.dispatch_parameters.model_dump_json(by_alias=True, exclude_none=True),
        )
    return json.dumps(result)


def build_enforcement_sections(model: AgentUniversalFormat) -> str:
    """Build security_boundary, implicit_grants, writing_output as JSON."""
    enforcement = model.enforcement
    sections = {}
    explicit = enforcement.enforcement_explicit_grants
    explicit_dump = json.loads(
        explicit.model_dump_json(by_alias=True, exclude_none=True),
    )
    if explicit_dump:
        sections["security_boundary"] = {
            "workspace_path": model.security.security_paths.security_paths_workspace.root,
            "capabilities": explicit_dump,
        }
    implicit = enforcement.enforcement_implicit_grants
    implicit_dump = json.loads(
        implicit.model_dump_json(by_alias=True, exclude_none=True),
    )
    if implicit_dump:
        sections["implicit_grants"] = {"capabilities": implicit_dump}
    tool = enforcement.enforcement_output_tool
    if tool is not None:
        tool_dump = json.loads(
            tool.model_dump_json(by_alias=True, exclude_none=True),
        )
        if tool_dump:
            sections["writing_output"] = {"writing_output": tool_dump}
    return json.dumps(sections)


def build_criteria_sections(model: AgentUniversalFormat) -> str:
    """Build constraints and anti_patterns sections as JSON."""
    guardrails = model.criteria.guardrails
    sections = {}
    if guardrails.guardrails_constraints is not None:
        sections["constraints"] = {
            "rules": [item.root for item in guardrails.guardrails_constraints.root],
        }
    if guardrails.guardrails_anti_patterns is not None:
        sections["anti_patterns"] = {
            "patterns": [item.root for item in guardrails.guardrails_anti_patterns.root],
        }
    return json.dumps(sections)


def build_execution_sections(model: AgentUniversalFormat) -> str:
    """Build instructions and examples sections as JSON."""
    execution = model.execution
    sections = {
        "instructions": {
            "steps": json.loads(
                execution.execution_instructions.model_dump_json(by_alias=True, exclude_none=True),
            ),
        },
    }
    if execution.execution_examples is not None:
        sections["examples"] = {
            "groups": json.loads(
                execution.execution_examples.model_dump_json(by_alias=True, exclude_none=True),
            ),
        }
    return json.dumps(sections)


def regroup(universal_json: str) -> str:
    """Regroup universal-format JSON into universal-render JSON."""
    model = AgentUniversalFormat.model_validate_json(universal_json)
    result = {
        "identity": json.loads(build_identity(model)),
        "input": json.loads(build_input_section(model)),
        "output": json.loads(build_output_section(model)),
        "return_format": json.loads(build_return_format(model)),
        "dispatcher": json.loads(build_dispatcher(model)),
    }
    result.update(json.loads(build_enforcement_sections(model)))
    result.update(json.loads(build_criteria_sections(model)))
    result.update(json.loads(build_execution_sections(model)))
    return json.dumps(result)
