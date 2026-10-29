from app.domain.degrees.prompt_builder import DegreePromptSpec


SPEC = DegreePromptSpec(
    name="M.Sc. Data Science",
    regulation=(
        "the local 2021 Studien- und Pruefungsordnung resources\n"
        "(FU-Mitteilungen 18/2021)"
    ),
    plan_check_scope="LP distribution, profile choice, Grundlagen modules, or elective selection",
    question_topics=(
        "LP requirements, the Grundlagenbereich, the profiles\n"
        "  (Data Science in Life Sciences / Data Science Technologies), elective pools,\n"
        "  or the Masterarbeit"
    ),
    offtopic_topics_de="Modulen, LP, Profilwahl und Studienplan-Regeln",
    offtopic_topics_en="modules, LP, profile choice, and study-plan rules",
    course_types={
        "vl": "lecture module",
        "seminar": "seminar module",
        "praktikum": "practical-course module",
    },
    thesis_name="Masterarbeit",
    study_plan_parser_note=(
        "matched against the official module catalogue and\n"
        "checked by deterministic Python rules"
    ),
)
