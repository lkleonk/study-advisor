"""Shared LLM prompt templates for all degrees.

Each degree's ``prompts.py`` declares only a ``DegreePromptSpec`` with its
degree-specific vocabulary; ``build_prompts`` renders the full prompt set from
the shared templates below. Change wording here once instead of per degree.
"""

from dataclasses import dataclass
from typing import Any

from app.domain.degrees.definition import DegreePrompts


@dataclass(frozen=True)
class DegreePromptSpec:
    # Short degree name, e.g. "M.Sc. Informatik"; prefixed with "FU Berlin".
    name: str
    # Regulation basis, e.g. "the local 2014 Studien- und Pruefungsordnung resources".
    regulation: str
    # What a plan check covers, completing "whether a concrete module plan ...".
    plan_check_scope: str
    # Rule topics, completing "the user asks about <name> rules, ...".
    question_topics: str
    # Topics for the off-topic redirect, e.g. "modules, LP, and study-plan rules".
    offtopic_topics_de: str
    offtopic_topics_en: str
    # Course-type ids used in this degree's offering tree -> short description.
    course_types: dict[str, str]
    # Thesis name for the generic study-plan parser ("Masterarbeit" / "Bachelorarbeit").
    thesis_name: str
    # Optional degree-specific additions, rendered as extra bullets / blocks.
    extra_selector_rules: tuple[str, ...] = ()
    selector_examples: str = ""
    extra_composer_rules: tuple[str, ...] = ()
    # Overrides for degrees with a richer study-plan parser (M.Sc. Informatik).
    study_plan_schema: dict[str, Any] | None = None
    study_plan_parser_rules: tuple[str, ...] | None = None
    # Extra parser context, e.g. which validator consumes the output.
    study_plan_parser_note: str = "checked by deterministic Python rules"
    # Extra keywords that mark a message as in scope for the heuristic fallback.
    fallback_domain_terms: tuple[str, ...] = ()


GENERIC_STUDY_PLAN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "modules": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "lp": {"type": "integer"},
                    "area": {"type": "string", "enum": ["thesis", "unknown"]},
                },
                "required": ["name", "lp", "area"],
            },
        },
    },
    "required": ["modules"],
}


LINK_RULES = """
- When the degree-rule context or course-offering context contains a URL that
  supports your answer (course catalogues, application forms, contact or info
  pages), include it inline as a Markdown link like
  [Vorlesungsverzeichnis](https://...) on the word it belongs to. Copy URLs
  exactly as given; never invent, shorten, or alter them. Only link http(s)
  URLs that literally appear in the context; never emit anchor links like
  (#section) or links to the degree-rule context. If the context contains no URL
  for the topic, answer without a link.
- Whenever you mention a resource that has a Markdown link in the context
  (Vorlesungsverzeichnis, application form, information page, MVS platform,
  contact page), attach that link to the mention. Never name a linked
  resource as plain text.
""".strip()


def _bullets(lines: tuple[str, ...]) -> str:
    return "\n".join(f"- {line}" for line in lines)


def _domain_scope(spec: DegreePromptSpec) -> str:
    return f"Domain: FU Berlin {spec.name} under {spec.regulation}."


def _answer_identity(spec: DegreePromptSpec) -> str:
    return (
        f"You are a study consultant for the FU Berlin {spec.name}.\n"
        f"You give advisory answers grounded in {spec.regulation}."
    )


def _classifier(spec: DegreePromptSpec, domain_scope: str) -> str:
    return f"""
{domain_scope}

Classify the latest user message into exactly one message_type:

- "plan_check": the user wants you to check whether a concrete module plan,
  {spec.plan_check_scope} satisfy the {spec.name} rules. Additions or
  corrections to a previously supplied plan are also plan_check.
- "degree_question": the user asks about {spec.name} rules, {spec.question_topics},
  and does not need a current course-offering lookup.
- "course_offering_question": the user asks which courses, lectures, seminars,
  practical courses, or projects are offered or available in a semester.
- "off_topic": the message is unrelated to FU Berlin {spec.name} study
  consulting.

Questions about taking or recognizing HU/TU courses are degree_question, not
course_offering_question; local course lookup covers FU semester offerings.

Also return include_cross_university_rules=true only when the latest question
concerns taking or recognizing courses at HU Berlin or TU Berlin,
Nebenhoererschaft/Zweithoererschaft, or is a contextual follow-up about that
topic. Otherwise return false. Use earlier messages only to resolve what the
latest user message refers to.

Return valid JSON only.
""".strip()


def _course_key_selector(spec: DegreePromptSpec, domain_scope: str) -> str:
    course_types = "\n".join(
        f"- {type_id}: {description}" for type_id, description in spec.course_types.items()
    )
    rules = (
        "You normally receive only course_offering_question messages.",
        "If a degree-rule question reaches this node by mistake, output an empty keys\n"
        "  array and needs_clarification=false.",
        "Do not filter by course title. The next node receives whole buckets and will\n"
        "  inspect the course titles inside those buckets.",
        "If the user asks about course offerings but gives no semester, ask a short\n"
        "  clarification question.",
        "If semester + course type are given but no area, output all matching area\n"
        "  buckets for that semester and course type.",
        "If semester + area are given but no course type, output all course-type\n"
        "  buckets for that semester and area.",
        "If semester is given but neither area nor course type is given, output all\n"
        "  buckets for that semester.",
        "If a course name is given, still output bucket keys, not a course-specific\n"
        "  slug.",
        *spec.extra_selector_rules,
    )
    examples = f"\nExamples:\n{spec.selector_examples.strip()}\n" if spec.selector_examples.strip() else ""
    # Doubled braces survive the f-string as the {placeholders} the
    # course_key_selector node fills via str.replace.
    return f"""
{domain_scope}

You select exact course-offering lookup buckets from the local course offerings
tree. The lookup key format is:

semester/area/course_type

Only output keys that are present in the tree below. Do not invent keys.

Course types:
{course_types}

Selection rules:
{_bullets(rules)}

Semester coverage:
{{semester_coverage_note}}
{examples}
Tree:
{{course_tree}}

Return valid JSON only.
""".strip()


def _study_plan_parser(spec: DegreePromptSpec, domain_scope: str) -> str:
    rules = spec.study_plan_parser_rules or (
        "Do not invent modules.",
        "Use the official module title where it is recognizable.",
        "If LP is explicit, extract it as an integer; otherwise use 0.",
        f'Set area "thesis" only for the {spec.thesis_name}; use "unknown" for everything\n'
        "  else. Do not classify modules into areas yourself.",
    )
    return f"""
{domain_scope}

Extract a structured study plan from the user's message. This is not the final
answer. The output will be {spec.study_plan_parser_note}.

Rules:
{_bullets(rules)}

Return valid JSON only.
""".strip()


def _answer_composer(spec: DegreePromptSpec, answer_identity: str, plan_validation_enabled: bool) -> str:
    rule_check_input = (
        "3. Deterministic rule-check results (only for plan checks). Trust its LP\n"
        "   totals over your own counting."
        if plan_validation_enabled
        else "3. A rule-check note: automatic study-plan validation is not available for\n"
        "   this degree. Follow that note; never present a plan as verified."
    )
    rules = (
        "Answer in the same language as the user.",
        "Do not invent Studien- or Pruefungsordnung rules beyond the supplied\n"
        "  degree-rule context.",
        "If the user asks about a specific course/module not covered by the RULES or\n"
        "  the course-offering context, say the local resources do not contain enough\n"
        "  information.",
        "If the course-offering context says the course lookup needs clarification, ask the\n"
        "  clarification question and do not answer a different question.",
        "If the course-offering context says no local data is available, say so and\n"
        "  refer the user to the official FU Berlin Vorlesungsverzeichnis instead of\n"
        "  guessing.",
        "Course availability is limited to the locally supplied semester data; do not\n"
        "  infer availability in other semesters.",
        "Only claim that a module is offered in a semester (and when or where it takes\n"
        "  place) if it appears in the course-offering context. The module lists in the\n"
        "  degree-rule context state requirements, not what is offered; never list a module\n"
        "  as offered just because it appears there.",
        *spec.extra_composer_rules,
        'Only append the advisory disclaimer ("advisory; official FU documents and the\n'
        '  examination office remain authoritative") when the user is making a plan\n'
        "  decision or asking about their own study plan. Skip it for pure factual\n"
        "  lookups.",
    )
    return f"""
{answer_identity}

Use the relevant degree-rule context supplied with the user message as your
authoritative source for all degree rules, LP requirements, and structural
constraints. The course-offering context (when provided) covers exact local
course-offering buckets for this degree. Use it to answer which courses are
offered in a semester, not to override the rules.

Inputs you may receive:
1. Course-offering context (may be empty or a no-data notice)
2. A parsed study plan: the module list extracted from the user's messages or
   an uploaded transcript PDF. Use it to answer module-level follow-ups (e.g.
   whether a specific module is present or how it is counted).
{rule_check_input}

Length:
- For a single factual lookup (a number, a name, a yes/no), answer in 1-2 sentences.
- For a plan-check or multi-part question, answer in short bullet points.
- Never restate the question or list rules the user did not ask about.

Other rules:
{_bullets(rules)}
{LINK_RULES}

Return valid JSON only.
""".strip()


def build_prompts(spec: DegreePromptSpec, *, plan_validation_enabled: bool) -> DegreePrompts:
    domain_scope = _domain_scope(spec)
    answer_identity = _answer_identity(spec)
    return DegreePrompts(
        domain_scope=domain_scope,
        answer_identity=answer_identity,
        classifier_system_prompt=_classifier(spec, domain_scope),
        course_key_selector_template=_course_key_selector(spec, domain_scope),
        study_plan_parser_system_prompt=_study_plan_parser(spec, domain_scope),
        answer_composer_system_prompt=_answer_composer(spec, answer_identity, plan_validation_enabled),
        offtopic_reply_de=f"Ich kann bei Fragen zum FU Berlin {spec.name}, {spec.offtopic_topics_de} helfen.",
        offtopic_reply_en=f"I can help with FU Berlin {spec.name} questions about {spec.offtopic_topics_en}.",
        fallback_domain_terms=spec.fallback_domain_terms,
    )


def study_plan_schema(spec: DegreePromptSpec) -> dict[str, Any]:
    return spec.study_plan_schema or GENERIC_STUDY_PLAN_SCHEMA
