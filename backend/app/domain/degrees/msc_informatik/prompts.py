from app.domain.degrees.prompt_builder import DegreePromptSpec


STUDY_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "specialization_area": {
            "type": ["string", "null"],
            "enum": ["practical", "theoretical", "technical", None],
        },
        "modules": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "lp": {"type": "integer"},
                    "area": {
                        "type": "string",
                        "enum": ["practical", "theoretical", "technical", "application", "thesis", "unknown"],
                    },
                    "is_wahlbereich": {"type": "boolean"},
                    "is_ungraded": {"type": "boolean"},
                    "is_bachelor_module": {"type": "boolean"},
                    "is_scientific_work": {"type": "boolean"},
                    "is_software_project": {"type": "boolean"},
                },
                "required": [
                    "name",
                    "lp",
                    "area",
                    "is_wahlbereich",
                    "is_ungraded",
                    "is_bachelor_module",
                    "is_scientific_work",
                    "is_software_project",
                ],
            },
        },
    },
    "required": ["specialization_area", "modules"],
}


SELECTOR_EXAMPLES = """
- User: "Welche Softwareprojekte gibt es im SoSe 2026?"
  Output: {"keys":["sose26/technical/swp","sose26/practical/swp","sose26/theoretical/swp"],"needs_clarification":false,"clarification_question":""}
- User: "technical courses in sose26"
  Output: {"keys":["sose26/technical/vl","sose26/technical/swp","sose26/technical/seminar"],"needs_clarification":false,"clarification_question":""}
- User: "Is Telematik offered in SoSe 2026?"
  Output: {"keys":["sose26/technical/vl","sose26/technical/swp","sose26/technical/seminar","sose26/practical/vl","sose26/practical/swp","sose26/practical/seminar","sose26/theoretical/vl","sose26/theoretical/swp","sose26/theoretical/seminar"],"needs_clarification":false,"clarification_question":""}
"""


SPEC = DegreePromptSpec(
    name="Master Informatik",
    regulation="the local 2014 Studien- und Pruefungsordnung resources",
    plan_check_scope=(
        "LP distribution, specialization, seminars, projects, or ungraded/Bachelor\n"
        "  module totals"
    ),
    question_topics=(
        "LP requirements, limits, specialization,\n"
        "  Wissenschaftliches Arbeiten, Softwareprojekt, Anwendungsbereich, or the checklist"
    ),
    offtopic_topics_de="Modulen, LP, Vertiefung und Studienplan-Regeln",
    offtopic_topics_en="modules, LP, specialization, and study-plan rules",
    course_types={
        "vl": "Vorlesung/lecture bucket",
        "swp": "Softwareprojekt bucket",
        "seminar": "seminar/Wissenschaftliches-Arbeiten bucket",
    },
    thesis_name="Masterarbeit",
    extra_selector_rules=(
        'Do not use "::", and do not output old slug-style keys such as\n'
        '  "sose26-tec-swp". Example: "Telematik in SoSe 2026" should select relevant\n'
        '  SoSe 2026 buckets, not "sose26-telematik".',
    ),
    selector_examples=SELECTOR_EXAMPLES,
    study_plan_schema=STUDY_PLAN_SCHEMA,
    study_plan_parser_rules=(
        "Do not invent modules.",
        "If a module area is explicit, use one of: practical, theoretical, technical,\n"
        "  application, thesis, unknown.",
        "If the user explicitly places a module in Wahlbereich/elective area, keep the\n"
        "  subject area when known and set is_wahlbereich=true.",
        "If LP is explicit, extract it as an integer.",
        "If the user states a specialization/Vertiefung, set specialization_area to\n"
        "  practical, theoretical, or technical.",
        "Mark Wissenschaftliches Arbeiten modules as is_scientific_work=true.",
        "Mark Softwareprojekt modules as is_software_project=true.",
        "Mark ungraded/non-differentiated modules as is_ungraded=true when stated or\n"
        "  obvious from the module name.",
        "Mark Bachelor modules as is_bachelor_module=true when stated.",
    ),
)
