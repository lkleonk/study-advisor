from app.domain.degrees.prompt_builder import DegreePromptSpec


SPEC = DegreePromptSpec(
    name="B.Sc. Informatik",
    regulation="the 2023 Studien- und Pruefungsordnung (FU-Mitteilungen 23/2023)",
    plan_check_scope="LP distribution, compulsory-elective choice, or ABV selection",
    question_topics=(
        "LP requirements, compulsory modules,\n"
        "  compulsory-elective modules, ABV, internship, or thesis"
    ),
    offtopic_topics_de="Modulen, LP und Studienregeln",
    offtopic_topics_en="modules, LP, and degree rules",
    course_types={
        "vl": "lecture module",
        "praktikum": "practical-course module",
        "seminar": "Wissenschaftliches Arbeiten seminar/proseminar module",
    },
    thesis_name="Bachelorarbeit",
    extra_selector_rules=(
        "Free-elective offerings are candidates only; never state that their credits\n"
        "  are automatically recognised.",
    ),
    extra_composer_rules=(
        "Treat free-elective course listings as candidates only: recognition,\n"
        "  relevance, and no-content-overlap remain subject to the regulation and\n"
        "  advising.",
    ),
)
