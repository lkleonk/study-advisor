from app.services.nodes.utils import degree_for, latest_user_message, looks_german
from app.services.states.consultant_state import ConsultantState
from app.services.wizardflow_service import node_scope


async def offtopic_node(state: ConsultantState) -> ConsultantState:
    with node_scope(state.get("wizardflow_message_id"), "offtopic", kind=None) as node:
        prompts = degree_for(state).prompts
        message = latest_user_message(state)
        node.log("node_input", {"message": message})
        reply = prompts.offtopic_reply_de if looks_german(message) else prompts.offtopic_reply_en
        result: ConsultantState = {
            "reply": reply,
            "messages": [{"role": "assistant", "content": reply}],
        }
        node.log("node_output", result)
        return result
