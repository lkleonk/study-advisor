from app.domain.degrees.prompt_builder import DegreePromptSpec


SPEC = DegreePromptSpec(
    name="B.Sc. Physik",
    regulation="the 2024 Studien- und Pruefungsordnung (FU-Mitteilungen 12/2024)",
    plan_check_scope="LP distribution, Wahlpflicht choice, or ABV selection",
    question_topics=(
        "LP requirements, compulsory modules,\n"
        "  Wahlpflicht modules, Praktika, ABV, Berufspraktikum, or the Bachelorarbeit"
    ),
    offtopic_topics_de="Modulen, LP und Studienregeln",
    offtopic_topics_en="modules, LP, and degree rules",
    course_types={
        "vl": "lecture module (Vorlesung with Übung)",
        "praktikum": "lab-course module (Praktikum)",
        "seminar": "seminar module",
    },
    thesis_name="Bachelorarbeit",
    fallback_domain_terms=("physik", "physics", "praktikum", "wahlpflicht", "bachelorarbeit"),
)
