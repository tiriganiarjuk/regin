"""Regroup identity and dispatcher sections.

Both consume indirect.metadata (agent_name, agent_description).
Identity: who the agent is + capability tier.
Dispatcher: how to launch and feed the agent.

Pure — receives typed model, returns typed model. No IO.
"""

from regin.structures.schema.agent_universal_format import AgentUniversalFormat
from regin.structures.schema import agent_universal_render as render


def regroup_identity(source: AgentUniversalFormat) -> render.Identity:
    """Assemble identity from indirect.metadata + task.role + task.processing."""
    name = source.indirect.metadata.agent_name.root
    title = " ".join(word.capitalize() for word in name.split("-"))
    role = source.task.role
    return render.Identity(
        title=render.TitleString(title),
        description=render.AgentDescription(source.indirect.metadata.agent_description.root),
        role_identity=render.StringText(role.role_identity.root),
        role_responsibility=render.RoleResponsibility(role.role_responsibility.root),
        capability_tier=render.AgentCapabilityTier(source.task.processing.capability_model.value),
        role_description=render.RoleDescription(role.role_description.root) if role.role_description else None,
        role_expertise=render.RoleExpertise.model_validate_json(
            role.role_expertise.model_dump_json(by_alias=True)
        ) if role.role_expertise else None,
    )


def regroup_dispatcher(source: AgentUniversalFormat) -> render.Dispatcher:
    """Assemble dispatcher from indirect + task.processing + task.return."""
    meta = source.indirect.metadata
    dispatch = source.indirect.dispatch
    proc = source.task.processing
    ret = source.task.return_
    return render.Dispatcher(
        agent_name=render.AgentName(meta.agent_name.root),
        agent_description=render.AgentDescription(meta.agent_description.root),
        dispatch_mode=render.DispatchMode(dispatch.dispatch_mode.value),
        background_mode=render.DispatchBackgroundMode(dispatch.dispatch_background_mode.value),
        input_format=render.DispatchInputFormat(dispatch.dispatch_input_format.value),
        input_delivery=render.DispatchInputDelivery(dispatch.dispatch_input_delivery.value),
        input_description=render.InputDescription(dispatch.dispatch_input_description.root),
        output_format=render.OutputFormatKind(proc.output_file_format.value),
        output_name_known=render.OutputNameKnown(proc.output_file_name_known.value),
        return_mode=render.ReturnMode(ret.return_mode.value),
        max_agents=render.Integer(dispatch.dispatch_max_agents.root) if dispatch.dispatch_max_agents else None,
        batch_size=render.DispatchBatchSize.model_validate_json(
            dispatch.dispatch_batch_size.model_dump_json(by_alias=True)
        ) if dispatch.dispatch_batch_size else None,
        parameters=render.DispatchParameters.model_validate_json(
            dispatch.dispatch_parameters.model_dump_json(by_alias=True)
        ) if dispatch.dispatch_parameters else None,
    )
