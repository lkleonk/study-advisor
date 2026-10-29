from app.domain.degrees.prompt_builder import DegreePromptSpec


SPEC = DegreePromptSpec(
    name="M.Sc. Physik",
    regulation="the 2024 Studien- und Pruefungsordnung (FU-Mitteilungen 12/2024)",
    plan_check_scope="LP distribution, Wahlpflicht choice, or Wahlbereich selection",
    question_topics=(
        "LP requirements, compulsory modules,\n"
        "  Wahlpflicht modules, the Wahlbereich, the research phase, the double master\n"
        "  with Institut Polytechnique, or the Masterarbeit"
    ),
    offtopic_topics_de="Modulen, LP und Studienregeln",
    offtopic_topics_en="modules, LP, and degree rules",
    course_types={
        "vl": "lecture module (lecture with tutorial)",
        "praktikum": "lab-course module",
        "seminar": "seminar module",
    },
    thesis_name="Masterarbeit",
    fallback_domain_terms=(
        "physik",
        "physics",
        "praktikum",
        "laboratory",
        "wahlpflicht",
        "wahlbereich",
        "elective",
        "research phase",
        "forschungsphase",
        "masterarbeit",
        "master thesis",
    ),
)
