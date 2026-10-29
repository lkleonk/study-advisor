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
                    "counted_in_bachelor": {"type": ["boolean", "null"]},
                    "used_for_master_admission": {"type": ["boolean", "null"]},
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
                    "counted_in_bachelor",
                    "used_for_master_admission",
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
        "  Wissenschaftliches Arbeiten, Softwareprojekt, Anwendungsbereich, the checklist,\n"
        "  rebooking completed modules, recognition of professional work, exam registration,\n"
        "  exam attempts, grade improvement, or study abroad"
    ),
    offtopic_topics_de="Modulen, LP, Vertiefung und Studienplan-Regeln",
    offtopic_topics_en="modules, LP, specialization, and study-plan rules",
    course_types={
        "vl": "Vorlesung/lecture bucket",
        "swp": "Softwareprojekt bucket",
        "seminar": "seminar/Wissenschaftliches-Arbeiten bucket",
    },
    thesis_name="Masterarbeit",
    fallback_domain_terms=(
        "umbuch", "rebook", "notenverbesserung", "grade improvement", "pruefungsanmeldung",
        "pruefungsversuch", "exam registration", "exam attempt", "retake", "whiteboard",
        "campus management", "auslandsstudium", "study abroad", "berufserfahrung",
        "professional experience", "work experience", "anerkennung", "anrechnung",
    ),
    extra_selector_rules=(
        'Do not use "::", and do not output old slug-style keys such as\n'
        '  "sose26-tec-swp". Example: "Telematik in SoSe 2026" should select relevant\n'
        '  SoSe 2026 buckets, not "sose26-telematik".',
    ),
    selector_examples=SELECTOR_EXAMPLES,
    study_plan_schema=STUDY_PLAN_SCHEMA,
    extra_composer_rules=(
        "Explain the degree as 70 LP Informatik, 10 LP Anwendungsbereich, 10 LP\n"
        "  Wahlbereich, and 30 LP Masterarbeit. Never fold Wahlbereich into the\n"
        "  other area totals or count its credits toward specialization minima.",
        "Seminar and Softwareprojekt limits apply across the whole plan, including\n"
        "  Wahlbereich. Wahlbereich never permits a third project or fifth seminar.",
        "Distinguish Bachelor-level modules from credits already used for a Bachelor\n"
        "  degree or Master admission. Unknown credit history needs confirmation;\n"
        "  do not infer eligibility from the 15 LP cap alone.",
        "For course-placement advice, check the supplied canonical checklist module\n"
        "  slots and module_catalog_name first. Prefer a suitable dedicated named\n"
        "  module over a broad slot when approved and consistent with the plan;\n"
        "  explain that alternative courses can fit a module without creating\n"
        "  additional copies of that module.",
        "Before proposing a broad module slot, consider which slots are already used\n"
        "  and courses the student wants in later semesters. Keep flexible slots\n"
        "  available for those courses where possible; ask for missing preferences\n"
        "  and mapping information, and state assumptions in provisional advice.\n"
        "  Do not invent future offerings or silently change the student's plan.",
        "External courses may be proposed for recognition against matching module\n"
        "  learning outcomes and workload. Help justify the target module, but do\n"
        "  not treat thematic fit, a matching name, or an arithmetic validation\n"
        "  result as official recognition. Refer the decision to the Prüfungsausschuss.",
        "Before suggesting rebooking, distinguish planned courses from completed\n"
        "  modules and ask about recorded grading if unknown. Apply the supplied\n"
        "  rebooking restriction; never suggest freeing a completed graded module\n"
        "  slot by moving its credit to another module.",
        "Professional-work recognition, actual exam registrations and attempts,\n"
        "  grade-improvement eligibility, and study-abroad agreements are not\n"
        "  established by an arithmetic plan check. Explain their supplied rules\n"
        "  and request missing facts; do not assume approval or completed bookings.\n"
        "  Distinguish FU exam procedures from those of a host university.",
    ),
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
        "Mark is_bachelor_module=true only for Bachelor-level modules. A Master-level\n"
        "  module taken during Bachelor enrollment is not a Bachelor-level module.",
        "For each module, set counted_in_bachelor and used_for_master_admission\n"
        "  only from explicit information; otherwise use null. A Bachelor-level\n"
        "  module is not automatically a module already counted in a Bachelor degree.",
        "If a module was part of the Bachelor degree (including a Master-level\n"
        "  module taken in the Bachelor), set counted_in_bachelor=true. If it was\n"
        "  used to meet Master admission requirements, set used_for_master_admission=true.",
        "Extra credits explicitly outside the completed Bachelor degree (normally\n"
        "  the 180 LP) have counted_in_bachelor=false; keep admission use null\n"
        "  unless the user also clarifies it. Do not add a historical Bachelor\n"
        "  transcript's modules to the Master plan unless they are proposed for credit.",
        "Wahlbereich is a separate 10 LP allocation. Never automatically mark\n"
        "  surplus Informatik or Anwendungsbereich modules as Wahlbereich; if\n"
        "  their allocation is unspecified, leave it for clarification.",
    ),
)
