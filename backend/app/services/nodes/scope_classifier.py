import logging
import re

from app.services.agent_config import agent_flow_config
from app.services.model_service import ModelService
from app.services.quota_service import DailyQuotaExceeded
from app.services.nodes.utils import (
    degree_for,
    format_recent_messages,
    latest_user_message,
    parse_json_content,
    recent_messages,
)
from app.services.states.consultant_state import ConsultantState
from app.services.wizardflow_service import node_scope


logger = logging.getLogger(__name__)


CLASSIFIER_SCHEMA = {
    "type": "object",
    "properties": {
        "message_type": {
            "type": "string",
            "enum": ["degree_question", "course_offering_question", "plan_check", "off_topic"],
        },
        "include_cross_university_rules": {"type": "boolean"},
    },
    "required": ["message_type", "include_cross_university_rules"],
}


def heuristic_classify(message: str, extra_domain_terms: tuple[str, ...] = ()) -> str:
    lowered = _normalize_text(message)
    plan_intent_terms = [
        "pruef",
        "check",
        "passt",
        "valid",
        "studienplan",
        "study plan",
        "module plan",
        "forgot",
        "vergessen",
        "add to my plan",
        "hinzufuegen",
    ]
    domain_terms = [
        "informatik",
        "master",
        "computer science",
        "cs",
        "technical",
        "technisch",
        "practical",
        "praktisch",
        "theoretical",
        "theoretisch",
        "lp",
        "credit",
        "credits",
        "ects",
        "vertiefung",
        "wissenschaftliches arbeiten",
        "softwareprojekt",
        "software project",
        "anwendungsbereich",
        "nebenfach",
        "unbenotet",
        "bachelormodul",
        "fu berlin",
        "studienplan",
        "bachelor",
        "modul",
        "abv",
        *extra_domain_terms,
    ]
    has_domain_signal = any(term in lowered for term in domain_terms)
    has_concrete_lp_list = lowered.count(" lp") >= 3

    if (any(term in lowered for term in plan_intent_terms) or has_concrete_lp_list) and has_domain_signal:
        return "plan_check"
    if heuristic_needs_cross_university_rules(lowered):
        return "degree_question"
    if _looks_like_degree_rule_question(lowered) and has_domain_signal:
        return "degree_question"
    if _looks_like_course_offering_question(lowered):
        return "course_offering_question"
    if has_domain_signal:
        return "degree_question"
    return "off_topic"


def heuristic_needs_cross_university_rules(message: str) -> bool:
    text = _normalize_text(message)
    phrases = [
        "hu berlin",
        "tu berlin",
        "humboldt-universitaet",
        "humboldt universitaet",
        "technische universitaet berlin",
        "nebenhoer",
        "zweithoer",
        "cross-registr",
        "cross registr",
        "partner university",
        "partneruniversitaet",
    ]
    return any(phrase in text for phrase in phrases)


def _looks_like_degree_rule_question(text: str) -> bool:
    patterns = [
        r"\bhow many\b.*\b(can|may|allowed|take|count|counts|required|need|needed)\b",
        r"\bhow much\b.*\b(lp|credit|credits)\b",
        r"\bwie viele\b.*\b(darf|kann|zaehlen|belegen|machen|brauche|benoetige)\b",
        r"\bwie viel\b.*\b(lp|leistungspunkt|leistungspunkte|credits?)\b",
        r"\b(at most|at least|maximum|minimum)\b",
        r"\b(max|min)\.?\b",
        r"\b(allowed|erlaubt|required|requirement|requirements|brauche|benoetige|muss|must)\b",
        r"\b(wahlbereich|core|kernbereich|regel|rules?)\b",
    ]
    return any(re.search(pattern, text) for pattern in patterns)


def _looks_like_course_offering_question(text: str) -> bool:
    offering_terms = [
        "angebot",
        "angeboten",
        "available",
        "course offerings",
        "findet",
        "gibt es",
        "kurse",
        "courses",
        "lecture",
        "lectures",
        "lehrveranstaltungen",
        "offered",
        "veranstaltungen",
    ]
    semester_pattern = r"\b(sose|ss|wise|ws|sommersemester|wintersemester|summer|winter)\s*[0-9]{2,4}\b"
    course_type_terms = [
        "softwareprojekt",
        "software project",
        "seminar",
        "wissenschaftliches arbeiten",
        "vorlesung",
        "lecture",
        "course",
        "courses",
    ]
    return any(term in text for term in offering_terms) or (
        bool(re.search(semester_pattern, text)) and any(term in text for term in course_type_terms)
    )


def _normalize_text(text: str) -> str:
    lowered = text.lower()
    replacements = {
        "\u00fc": "ue",
        "\u00e4": "ae",
        "\u00f6": "oe",
        "\u00df": "ss",
        "\u00c3\u00bc": "ue",
        "\u00c3\u00a4": "ae",
        "\u00c3\u00b6": "oe",
    }
    for source, target in replacements.items():
        lowered = lowered.replace(source, target)
    return lowered


async def scope_classifier_node(state: ConsultantState) -> ConsultantState:
    with node_scope(state.get("wizardflow_message_id"), "scope_classifier", kind='llm') as node:
        logger.info("Scope classifier invoked")
        degree = degree_for(state)
        classifier_prompt = degree.prompts.classifier_system_prompt
        message = latest_user_message(state)
        conversation = format_recent_messages(
            recent_messages(state, agent_flow_config.scope_classifier.history_turns)
        )
        llm_message = f"Classify the latest user message in this recent conversation:\n{conversation}"
        fallback = heuristic_classify(message, degree.prompts.fallback_domain_terms)
        fallback_cross_university = heuristic_needs_cross_university_rules(conversation)
        source = "heuristic"

        node.log("node_input", message)
        node.log("llm_input", {"prompt": classifier_prompt, "msg": llm_message})
        try:
            response = await ModelService().invoke(
                prompt=classifier_prompt,
                message=llm_message,
                format=CLASSIFIER_SCHEMA,
            )
            response_content = response.get("content", "")
            node.log("llm_output", response_content)
            data = parse_json_content(response_content)
            message_type = data.get("message_type")
            include_cross_university_rules = data.get("include_cross_university_rules")
            if message_type not in {"degree_question", "course_offering_question", "plan_check", "off_topic"}:
                message_type = fallback
                source = "heuristic_invalid_llm_output"
            else:
                source = "llm"
            if not isinstance(include_cross_university_rules, bool):
                include_cross_university_rules = fallback_cross_university
                source = f"{source}_heuristic_cross_university_flag"
        except DailyQuotaExceeded:
            raise
        except Exception as exc:
            node.log("llm_error", {"type": type(exc).__name__, "message": str(exc)})
            logger.exception("Classifier failed; using heuristic fallback.")
            message_type = fallback
            include_cross_university_rules = fallback_cross_university

        if message_type == "plan_check" and not degree.plan_validation_enabled:
            # No trusted validator for this degree: answer as a degree question.
            message_type = "degree_question"
            source = f"{source}_plan_validation_disabled"

        logger.info(
            "Scope classifier chose message_type=%s include_cross_university_rules=%s source=%s",
            message_type,
            include_cross_university_rules,
            source,
        )
        result: ConsultantState = {
            "message_type": message_type,
            "include_cross_university_rules": include_cross_university_rules,
        }
        node.log("node_output", {
                "message_type": message_type,
                "include_cross_university_rules": include_cross_university_rules,
                "source": source,
            })
        return result
