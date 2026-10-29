from app.domain.degrees.prompt_builder import DegreePromptSpec


SPEC = DegreePromptSpec(
    name="B.Sc. Bioinformatik",
    regulation="the 2023 Studien- und Pruefungsordnung (FU-Mitteilungen 34/2023)",
    plan_check_scope="LP distribution, Wahlbereich choice, or ABV selection",
    question_topics=(
        "LP requirements, compulsory modules in\n"
        "  Informatik, Mathematik/Statistik, or Biologie/Chemie, the Wahlbereich, ABV,\n"
        "  Berufspraktikum, or the Bachelorarbeit"
    ),
    offtopic_topics_de="Modulen, LP und Studienregeln",
    offtopic_topics_en="modules, LP, and degree rules",
    course_types={
        "vl": "lecture module (Vorlesung, usually with Übung)",
        "praktikum": "practical-course module (Praktikum or Kurs)",
        "seminar": "seminar, e.g. the seminar part of Wissenschaftliches Arbeiten",
    },
    thesis_name="Bachelorarbeit",
    extra_selector_rules=(
        "Wahlbereich and free-ABV offerings are examples only; never state that\n"
        "  other modules are automatically recognised.",
    ),
    extra_composer_rules=(
        "Treat Wahlbereich and free-ABV course listings as examples: apart from the\n"
        "  recommended modules, recognition needs approval by the Prüfungsausschuss.",
    ),
    fallback_domain_terms=("bioinformatik", "bioinformatics", "wahlbereich", "berufspraktikum", "bachelorarbeit"),
)
