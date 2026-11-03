from app.domain.degrees.prompt_builder import DegreePromptSpec


SPEC = DegreePromptSpec(
    name="M.Sc. Computational Sciences",
    regulation=(
        "the 2025 Studien- und Pruefungsordnung (FU-Mitteilungen 21/2025), amended by "
        "FU-Mitteilungen 27/2026"
    ),
    plan_check_scope="LP distribution, Synchronisierung choice, Scientific Computing A/B pairing, or specialisation offers",
    question_topics=(
        "LP requirements, the Synchronisierungsbereich, the Scientific\n"
        "  Computing A/B modules, the specialisations (Molecular, Geo, Atmospheric\n"
        "  Sciences), the EUMaster4HPC double master, or the Masterarbeit"
    ),
    offtopic_topics_de="Modulen, LP und Studienregeln",
    offtopic_topics_en="modules, LP, and degree rules",
    course_types={
        "vl": "lecture module (lecture with tutorial)",
        "seminar": "seminar module",
        "praktikum": "project or lab module",
    },
    thesis_name="Masterarbeit",
    fallback_domain_terms=(
        "computational sciences",
        "scientific computing",
        "synchronisierung",
        "synchronisation",
        "synchronization",
        "spezialisierung",
        "specialisation",
        "specialization",
        "molecular sciences",
        "geosciences",
        "atmospheric sciences",
        "scientific project",
        "eumaster4hpc",
        "high performance computing",
        "masterarbeit",
        "master thesis",
    ),
)
