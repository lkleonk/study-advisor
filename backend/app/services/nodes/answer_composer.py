import json
import logging

from app.domain.program_rules import CROSS_UNIVERSITY_RULE_SECTION_ID, render_rules_context
from app.services.agent_config import agent_flow_config
from app.services.model_service import ModelService
from app.services.quota_service import DailyQuotaExceeded
from app.services.nodes.utils import (
    ADVISORY_DISCLAIMER_DE,
    ADVISORY_DISCLAIMER_EN,
    degree_for,
    format_recent_messages,
    latest_user_message,
    looks_german,
    parse_json_content,
    recent_messages,
    sanitize_reply_links,
    strip_advisory_disclaimer,
)
from app.services.states.consultant_state import ConsultantState
from app.services.wizardflow_service import node_scope


logger = logging.getLogger(__name__)


class AnswerGenerationError(RuntimeError):
    """Raised when the answer composer cannot produce a real answer."""


NO_PLAN_VALIDATION_NOTE = (
    "(Automatic study-plan validation is not available for this degree. Do not state "
    "whether a plan or transcript satisfies the degree rules or how many LP are still "
    "missing as a verified fact. You may explain the relevant rules and compare them "
    "with the listed modules as orientation only, and recommend confirming with the "
    "examination office / Studienberatung.)"
)


ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {"type": "string"},
    },
    "required": ["message"],
}


async def answer_composer_node(state: ConsultantState) -> ConsultantState:
    with node_scope(state.get("wizardflow_message_id"), "answer_composer", kind='llm') as node:
        logger.info("Answer composer invoked")
        degree = degree_for(state)
        composer_prompt = degree.prompts.answer_composer_system_prompt
        excluded_rule_sections = (
            set()
            if state.get("include_cross_university_rules")
            else {CROSS_UNIVERSITY_RULE_SECTION_ID}
        )
        rules_context = render_rules_context(
            degree.get_program_rules(),
            exclude_section_ids=excluded_rule_sections,
        )
        user_message = latest_user_message(state)
        history = format_recent_messages(
            recent_messages(state, agent_flow_config.answer_composer.history_turns)
        )
        context = state.get("course_context") or "(no course-offering context)"
        rule_result = state.get("rule_check_result") if degree.plan_validation_enabled else None
        parsed_plan = state.get("parsed_study_plan")
        rule_check_context = (
            json.dumps(rule_result, ensure_ascii=False, indent=2)
            if rule_result
            else "(not a plan check)"
            if degree.plan_validation_enabled
            else NO_PLAN_VALIDATION_NOTE
        )

        message = f"""
User message:
{user_message}

Recent conversation:
{history}

Relevant degree-rule context:
{rules_context}

Course-offering context:
{context}

Course lookup keys:
{json.dumps(state.get("course_lookup_keys") or [], ensure_ascii=False, indent=2)}

Parsed study plan (module list, e.g. from an uploaded transcript):
{json.dumps(parsed_plan, ensure_ascii=False, indent=2) if parsed_plan else "(no parsed study plan)"}

Deterministic rule-check result:
{rule_check_context}
""".strip()

        node.log("llm_input", {"prompt": composer_prompt, "msg": message})
        try:
            response = await ModelService().invoke(
                prompt=composer_prompt,
                message=message,
                format=ANSWER_SCHEMA,
            )
            response_content = response.get("content", "")
            node.log("llm_output", response_content)
            data = parse_json_content(response_content)
            reply = data.get("message") if isinstance(data, dict) else None
            if not isinstance(reply, str) or not reply.strip():
                raise AnswerGenerationError("The answer composer returned an empty response.")
        except DailyQuotaExceeded:
            raise
        except Exception as exc:
            node.log("llm_error", {"type": type(exc).__name__, "message": str(exc)})
            logger.exception("Answer composition failed.")
            if isinstance(exc, AnswerGenerationError):
                raise
            raise AnswerGenerationError("The answer composer failed to generate a response.") from exc

        reply = sanitize_reply_links(reply, f"{composer_prompt}\n{message}")
        reply, model_added_disclaimer = strip_advisory_disclaimer(reply)
        if model_added_disclaimer or state.get("message_type") == "plan_check":
            disclaimer = ADVISORY_DISCLAIMER_DE if looks_german(user_message) else ADVISORY_DISCLAIMER_EN
            reply = f"{reply}\n\n{disclaimer}"
        result: ConsultantState = {
            "reply": reply,
            "messages": [{"role": "assistant", "content": reply}],
        }
        node.log("node_output", result)
        return result
