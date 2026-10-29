from functools import lru_cache

from app.domain.program_rules import (
    CROSS_UNIVERSITY_RULE_SECTION_ID,
    ProgramRuleItem,
    ProgramRuleSection,
    ProgramRuleSource,
    ProgramRulesCatalogue,
)


STUDY_REGULATIONS = ProgramRuleSource(
    label="M.Sc. Physik Studien- und Pruefungsordnung 2024 (FU-Mitteilungen 12/2024, pp. 508-544)",
    path="https://www.fu-berlin.de/service/zuvdocs/amtsblatt/2024/ab122024.pdf",
)

CROSS_UNIVERSITY_SOURCES = [
    ProgramRuleSource(
        label="HU Berlin Gast- und Nebenhoererschaft",
        path="https://www.hu-berlin.de/studium/nach-dem-studium/lebenslanges-lernen/gasthoerer-und-nebenhoererschaft",
    ),
    ProgramRuleSource(
        label="TU Berlin Gast- und Nebenhoererschaft",
        path="https://www.tu.berlin/studierendensekretariat/themen-a-z/gast-und-nebenhoererschaft/",
    ),
    STUDY_REGULATIONS,
]

THEORETICAL_ELECTIVES = (
    "Advanced Quantum Mechanics",
    "Statistical Physics and Thermodynamics",
    "Advanced Statistical Physics",
    "Quantum Field Theory and Many-Body Physics",
)
EXPERIMENTAL_ELECTIVES = (
    "Advanced Solid State Physics",
    "Advanced Atomic and Molecular Physics",
    "Advanced Biophysics",
)

# Wahlbereich modules offered by the Fachbereich Physik (§ 7(2) Nr. 3 a).
RESEARCH_FOCUS_MODULES = (
    ("Theoretical Condensed Matter Physics", 10),
    ("Nanophysics", 5),
    ("Magnetism and Spin Electronics", 5),
    ("Surface Science", 5),
    ("Theory of Light-Matter Interaction", 10),
    ("Advanced Optics", 10),
    ("Ultrafast Spectroscopy and Nonlinear Optics", 5),
    ("Photobiophysics", 5),
    ("Special Topics in Molecular Biophysics", 5),
    ("Advanced Biospectroscopy", 5),
    ("Semiconductor Physics", 5),
    ("Advanced Astronomy and Astrophysics", 12),
    ("Quantum Information Theory", 10),
    ("Advanced Computational Physics", 10),
    ("Signal Analysis for Physicist", 8),
    ("Physics and Chemistry of Sustainability I - Renewable Energy", 5),
    ("Science Studies in Physics", 5),
    ("Science Studies Communication", 5),
    ("Modern Theoretical Physics A", 5),
    ("Modern Theoretical Physics B", 8),
    ("Modern Theoretical Physics C", 10),
    ("Modern Experimental Physics A", 5),
    ("Modern Experimental Physics B", 8),
    ("Modern Experimental Physics C", 10),
    ("Modern Physics: Scientific Presentation", 5),
)

STUDY_PLAN = (
    ("1st semester", "Advanced Laboratory Course (10 LP), Wahlpflicht module (10 LP), Wahlbereich (10 LP)"),
    ("2nd semester", "Selected Topics: Scientific Presentations (5 LP), Wahlpflicht module (10 LP), Wahlbereich (15 LP)"),
    ("3rd semester", "Research phase: Scientific Specialization (15 LP) and Methodology and Project Planning (15 LP)"),
    ("4th semester", "Masterarbeit with accompanying colloquium (30 LP)"),
)


@lru_cache(maxsize=1)
def get_program_rules() -> ProgramRulesCatalogue:
    return ProgramRulesCatalogue(
        degree_program="FU Berlin M.Sc. Physik",
        regulation="2024 study and examination regulations (FU-Mitteilungen 12/2024)",
        catalogue_version="msc-physik-2024-v1",
        source_note=(
            "Rules catalogue for the FU Berlin M.Sc. Physik under the 2024 regulations, which apply "
            "to students enrolled after they came into force. Official FU documents and the "
            "Prüfungsausschuss Physik remain authoritative."
        ),
        sections=[
            ProgramRuleSection(
                id="overall-structure",
                title="Overall Structure",
                description=(
                    "The degree comprises 120 LP over a standard duration of four semesters: a 60-LP "
                    "Studienphase and a 60-LP guided research phase that includes the 30-LP Masterarbeit (§ 7)."
                ),
                items=[
                    ProgramRuleItem(label="Total degree volume", text="120 LP total.", minimum=120, maximum=120, unit="LP"),
                    ProgramRuleItem(
                        label="Studienphase",
                        text="60 LP: Pflichtbereich 15 LP, Wahlpflichtbereich 20 LP, Wahlbereich 25 LP.",
                        minimum=60,
                        maximum=60,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Angeleitete Forschungsphase",
                        text="60 LP: Scientific Specialization (15 LP), Methodology and Project Planning (15 LP), Masterarbeit with colloquium (30 LP).",
                        minimum=60,
                        maximum=60,
                        unit="LP",
                    ),
                    ProgramRuleItem(label="Regelstudienzeit", text="Four semesters."),
                    ProgramRuleItem(
                        label="Language",
                        text=(
                            "Teaching and examinations are in English. With approval of the Prüfungsausschuss, "
                            "written work, lab reports, examinations, and the Masterarbeit can be done in German."
                        ),
                    ),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="compulsory-modules",
                title="Compulsory Modules (Pflichtbereich)",
                description="Both modules are mandatory, 15 LP in total. Neither has a module examination (ungraded).",
                items=[
                    ProgramRuleItem(
                        label="Advanced Laboratory Course",
                        text="Advanced Laboratory Course (10 LP): internal Praktikum and seminar, every semester, compulsory attendance.",
                        minimum=10,
                        maximum=10,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Selected Topics: Scientific Presentations",
                        text="Selected Topics: Scientific Presentations (5 LP): seminar, every semester, compulsory attendance.",
                        minimum=5,
                        maximum=5,
                        unit="LP",
                    ),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="compulsory-elective-modules",
                title="Compulsory-Elective Modules (Wahlpflichtbereich)",
                description=(
                    "Complete two 10-LP modules (20 LP). At least one of them must be from theoretical physics."
                ),
                items=[
                    ProgramRuleItem(label="Wahlpflicht volume", text="Two modules of 10 LP each.", minimum=20, maximum=20, unit="LP"),
                    ProgramRuleItem(
                        label="Theoretical physics (at least one)",
                        text=", ".join(THEORETICAL_ELECTIVES) + " (10 LP each).",
                    ),
                    ProgramRuleItem(
                        label="Experimental physics",
                        text=", ".join(EXPERIMENTAL_ELECTIVES) + " (10 LP each).",
                    ),
                    ProgramRuleItem(
                        label="Research-phase prerequisite",
                        text="The theoretical module is also an admission requirement for the research phase.",
                    ),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="elective-area",
                title="Elective Area (Wahlbereich)",
                description=(
                    "Complete modules totalling 25 LP to set an individual subject-specific, interdisciplinary, "
                    "or career-oriented focus."
                ),
                items=[
                    ProgramRuleItem(label="Wahlbereich volume", text="Modules totalling 25 LP.", minimum=25, maximum=25, unit="LP"),
                    ProgramRuleItem(
                        label="Research-focus modules of the Fachbereich Physik",
                        text=(
                            "; ".join(f"{name} ({lp} LP)" for name, lp in RESEARCH_FOCUS_MODULES)
                            + ". They are offered in irregular order; at least seven of them are offered each academic year."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Interdisciplinary modules",
                        text=(
                            "Instead, modules from mathematics and natural-science programmes of the Fachbereiche "
                            "Mathematik/Informatik, Biologie/Chemie/Pharmazie, and Geowissenschaften can be chosen if "
                            "access can be granted. The Prüfungsausschuss publishes a list of modules that need no "
                            "application; others require its approval. They must not be identical to modules taken "
                            "in the bachelor's degree."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Career-oriented modules",
                        text=(
                            "Graded modules from non-science subjects (e.g. Betriebswirtschaft or Philosophie) are "
                            "possible on a justified application to the Prüfungsausschuss explaining their relevance "
                            "to the degree's qualification goals."
                        ),
                    ),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="research-phase",
                title="Guided Research Phase",
                description=(
                    "In the third semester, Scientific Specialization and Methodology and Project Planning are taken "
                    "in parallel; then the Masterarbeit follows (§ 7(3))."
                ),
                items=[
                    ProgramRuleItem(
                        label="Admission requirement",
                        text=(
                            "Advanced Laboratory Course (10 LP), one theoretical-physics Wahlpflicht module (10 LP), "
                            "and further master's modules of at least 25 LP successfully completed."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Scientific Specialization",
                        text="15 LP, every semester: project module and seminar; graded scientific talk (about 30 minutes) with discussion.",
                        minimum=15,
                        maximum=15,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Methodology and Project Planning",
                        text="15 LP, every semester: project module and internal Praktikum with a written report of about 20 pages; no module examination (ungraded).",
                        minimum=15,
                        maximum=15,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="External research phase",
                        text=(
                            "With approval of the Prüfungsausschuss, the research-phase modules can be done at a suitable "
                            "external institution if supervision by an authorised examiner of the degree is ensured."
                        ),
                    ),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="masterarbeit",
                title="Masterarbeit",
                description="The Masterarbeit with accompanying colloquium counts as 30 LP (§ 10).",
                items=[
                    ProgramRuleItem(
                        label="Admission",
                        text=(
                            "Last enrolled in the M.Sc. Physik at FU Berlin. The application is submitted to the "
                            "Prüfungsausschuss before completing Scientific Specialization and Methodology and Project "
                            "Planning; the thesis topic should form a coherent unit with these modules. A confirmation "
                            "from a supervising examiner must be attached."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Working time",
                        text="Six months, starting after Scientific Specialization and Methodology and Project Planning are completed.",
                    ),
                    ProgramRuleItem(label="Expected length", text="About 60 pages including footnotes and bibliography."),
                    ProgramRuleItem(label="Topic return", text="The topic can be returned once within the first four weeks."),
                    ProgramRuleItem(label="Colloquium", text="One talk of about 30 minutes on the progress of the thesis."),
                    ProgramRuleItem(
                        label="Assessment",
                        text=(
                            "Two examiners, at least one of them a Hochschullehrer of the Fachbereich Physik; passed with "
                            "at least grade 4.0. With approval it can be written externally (company or research institution)."
                        ),
                    ),
                    ProgramRuleItem(label="Submission", text="Electronic submission as a machine-readable PDF with a declaration of independent work."),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="study-plan",
                title="Exemplary Study Plan",
                description=(
                    "Recommended sequence from Anlage 2.1. The modules of semesters 1 and 2 can be taken in any order; "
                    "an even workload across both semesters is recommended."
                ),
                items=[ProgramRuleItem(label=semester, text=modules) for semester, modules in STUDY_PLAN],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="examinations",
                title="Examinations and Repetition",
                description="Rules on repeating examinations and grade improvement (§ 11).",
                items=[
                    ProgramRuleItem(label="Failed examinations", text="A failed Masterarbeit may be repeated twice; other examinations may be repeated three times."),
                    ProgramRuleItem(
                        label="Grade improvement",
                        text=(
                            "A written exam passed with 4.0 or better may be repeated once to improve the grade, at the "
                            "latest at the start of the following semester; the better grade counts. Not possible for "
                            "repeat examinations."
                        ),
                    ),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="double-degree",
                title="Double Master with Institut Polytechnique de Paris",
                description=(
                    "Qualified students can apply for a Franco-German double master's programme with the Institut "
                    "Polytechnique de Paris, starting in a winter semester (§ 8)."
                ),
                items=[
                    ProgramRuleItem(label="Application", text="Usually after the first semester; the deadline is 30 April each year. A joint selection committee decides."),
                    ProgramRuleItem(
                        label="Structure",
                        text=(
                            "Studienphase at FU Berlin (all Pflicht modules; Statistical Physics and Thermodynamics is required "
                            "in the Wahlpflichtbereich unless an equivalent was taken in the bachelor's degree), then the research "
                            "phase at the Institut Polytechnique in an M2 programme (recommended: Materials Science and "
                            "Nano-Objects) including the Masterarbeit; 120 LP total."
                        ),
                    ),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="advising-and-abroad",
                title="Advising, Study Abroad, and Transition",
                description="Advising, recommended study-abroad window, and the transition from the 2020 regulations (§§ 4, 12, 14).",
                items=[
                    ProgramRuleItem(
                        label="Study advising",
                        text=(
                            "Studienfachberatung is provided by the lecturers of the Fachbereich Physik. Students who have "
                            "earned less than one third of the expected LP after half of the Regelstudienzeit are offered advising."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Study abroad",
                        text="Recommended in the second semester, based on a learning agreement with the Prüfungsausschuss chair; the master coordinators help with planning.",
                    ),
                    ProgramRuleItem(
                        label="Transition from the 2020 regulations",
                        text=(
                            "Students enrolled before these regulations came into force continue under the 2020 regulations "
                            "(FU-Mitteilungen 17/2020) unless they apply to switch (irrevocable). Graduating under the 2020 "
                            "regulations is possible until the end of SoSe 2027."
                        ),
                    ),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id=CROSS_UNIVERSITY_RULE_SECTION_ID,
                title="Courses at HU Berlin and TU Berlin (Nebenhörerschaft)",
                description=(
                    "Modules taken as a cross-registered student ('Nebenhörer', also called Zweithörerschaft) at "
                    "Humboldt-Universität or Technische Universität Berlin can be recognized on application to the "
                    "Prüfungsausschuss Physik, most directly in the Wahlbereich."
                ),
                items=[
                    ProgramRuleItem(
                        label="Enrollment as Nebenhörer",
                        text=(
                            "Ask the teacher of the HU/TU course for approval and submit the Nebenhörer application described "
                            "on the [HU Nebenhörerschaft page](https://www.hu-berlin.de/studium/nach-dem-studium/lebenslanges-lernen/gasthoerer-und-nebenhoererschaft) "
                            "or the [TU Nebenhörerschaft page](https://www.tu.berlin/studierendensekretariat/themen-a-z/gast-und-nebenhoererschaft/)."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Recognition at FU",
                        text=(
                            "Modules outside the published list need approval by the Prüfungsausschuss Physik; clarify "
                            "beforehand whether and how the module can count, then apply for recognition with the "
                            "Leistungsnachweis and the module description."
                        ),
                    ),
                    ProgramRuleItem(label="No double counting", text="Modules must not be identical to modules already taken in the bachelor's degree, and the same content counts only once."),
                ],
                sources=CROSS_UNIVERSITY_SOURCES,
            ),
        ],
    )
