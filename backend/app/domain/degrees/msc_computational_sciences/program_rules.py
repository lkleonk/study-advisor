from functools import lru_cache

from app.domain.program_rules import (
    CROSS_UNIVERSITY_RULE_SECTION_ID,
    ProgramRuleItem,
    ProgramRuleSection,
    ProgramRuleSource,
    ProgramRulesCatalogue,
)


STUDY_REGULATIONS = ProgramRuleSource(
    label="M.Sc. Computational Sciences Studien- und Pruefungsordnung 2025 (FU-Mitteilungen 21/2025, pp. 391-442)",
    path="https://www.fu-berlin.de/service/zuvdocs/amtsblatt/2025/ab212025.pdf",
)
AMENDMENT_2026 = ProgramRuleSource(
    label="Erste Aenderungsordnung 2026, EUMaster4HPC double master (FU-Mitteilungen 27/2026, pp. 715-721)",
    path="https://www.fu-berlin.de/service/zuvdocs/amtsblatt/2026/ab272026.pdf",
)
ADMISSION_REGULATIONS = ProgramRuleSource(
    label="M.Sc. Computational Sciences Zugangssatzung 2020 (FU-Mitteilungen 31/2020, pp. 525-528)",
    path="https://www.fu-berlin.de/service/zuvdocs/amtsblatt/2020/ab312020.pdf",
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

# Synchronisierungsbereich subject offers (§ 7(2) sentence 2). Modules without a
# description in Anlage 1 follow the regulations of their home programme.
SYNC_OFFERS = (
    ("Chemie", "Molekülspektroskopie (5 LP), Theoretische Chemie (5 LP), Quantenmechanische Beschreibung von Atomen und chemischer Bindung (10 LP)"),
    ("Geologische Wissenschaften", "Geological foundations (6 LP), Introduction to planetary sciences and planet formation (9 LP)"),
    ("Geographische Wissenschaften", "Einführung in die Klima- und Hydrogeographie (5 LP), Fernerkundung und Geomatik für Fortgeschrittene (10 LP), Principles of GIS and remote sensing (6 LP)"),
    ("Informatik", "Complex Algorithms A, Computer Science and Data Structures A, Computer Science and Fundamentals of Programming A (15 LP each)"),
    ("Mathematik", "Introduction to Numerical Mathematics A, Numerics of ODEs and numerical linear algebra A, Numerics of partial differential equations A, Synchronisierung Mathematik (15 LP each)"),
    ("Meteorologie", "Dynamik der Atmosphäre 1 (8 LP), Dynamik der Atmosphäre 2 (8 LP), Synoptische Meteorologie (7 LP)"),
    ("Physik", "Computational Statistical Physics I A, Computational Statistical Physics II A (15 LP each), Einführung in die Quantenmechanik (10 LP)"),
)

# Which subject offers fill the 15 elective Synchronisierung LP, by bachelor background (§ 7(2) sentence 4).
SYNC_BY_BACKGROUND = (
    ("Chemie, Geographische Wissenschaften, or Geologische Wissenschaften (chemical-biological sequence)", "Synchronisierung Mathematik (15 LP)."),
    ("Mathematik, Informatik, or engineering", "15 LP from Chemie, Geographische Wissenschaften, Geologische Wissenschaften, Meteorologie, or Physik."),
    ("Physik", "15 LP from Geographische Wissenschaften, Geologische Wissenschaften, Informatik, Mathematik, or Meteorologie."),
    ("Meteorologie", "15 LP from Chemie, Geographische Wissenschaften, Geologische Wissenschaften, Informatik, Mathematik, or Physik."),
    ("Geologische Wissenschaften (mathematical-physical sequence)", "15 LP from Chemie, Informatik, Mathematik, Meteorologie, or Physik."),
)

SC_INFORMATIK = ("Complex Algorithms", "Computer Science and Data Structures", "Computer Science and Fundamentals of Programming", "Fundamentals of Machine Learning")
SC_NUMERIK = (
    "Introduction to Numerical Mathematics",
    "Numerics of ODEs and numerical linear algebra",
    "Numerics of partial differential equations",
    "Discrete Mathematics I",
    "Discrete Mathematics II",
)
SC_STATISTIK = ("Computational Statistical Physics I", "Computational Statistical Physics II", "Probability Theory I", "Probability Theory II")

SPECIALISATION_ELECTIVES = "Advances in computational sciences, Selected topics in theoretical computational sciences, Selected topics in applied computational sciences (5 LP each, offered irregularly)"

STUDY_PLAN_A = (
    ("1st semester", "Computational Sciences (15 LP) and Synchronisierung elective module(s) (15 LP)"),
    ("2nd semester", "Scientific Computing module from Angebot A (15 LP) and from Angebot B (15 LP)"),
    ("3rd semester", "Specialisation area (30 LP)"),
    ("4th semester", "Masterarbeit with accompanying colloquium (30 LP)"),
)
STUDY_PLAN_B = (
    ("1st semester", "Computational Sciences (15 LP) and Scientific Computing module from Angebot B (15 LP)"),
    ("2nd semester", "Scientific Computing module from Angebot A (15 LP) and Synchronisierung elective module(s) (15 LP)"),
    ("3rd semester", "Specialisation area (30 LP)"),
    ("4th semester", "Masterarbeit with accompanying colloquium (30 LP)"),
)


def _variants(topics: tuple[str, ...]) -> str:
    return ", ".join(topics) + " (15 LP each)."


@lru_cache(maxsize=1)
def get_program_rules() -> ProgramRulesCatalogue:
    return ProgramRulesCatalogue(
        degree_program="FU Berlin M.Sc. Computational Sciences",
        regulation="2025 study and examination regulations (FU-Mitteilungen 21/2025), amended 2026 (FU-Mitteilungen 27/2026)",
        catalogue_version="msc-computational-sciences-2025-v1",
        source_note=(
            "Rules catalogue for the joint FU Berlin M.Sc. Computational Sciences (Fachbereiche Biologie/Chemie/"
            "Pharmazie, Geowissenschaften, Mathematik/Informatik, and Physik) under the 2025 regulations, which apply "
            "to students enrolled from WiSe 2025/26, including the 2026 amendment. Section numbers follow the amended "
            "text. Official FU documents and the Prüfungsausschuss Computational Sciences remain authoritative."
        ),
        sections=[
            ProgramRuleSection(
                id="overall-structure",
                title="Overall Structure",
                description="The degree comprises 120 LP over a standard duration of four semesters, split into four 30-LP parts (§ 7).",
                items=[
                    ProgramRuleItem(label="Total degree volume", text="120 LP total.", minimum=120, maximum=120, unit="LP"),
                    ProgramRuleItem(
                        label="Synchronisierungsbereich",
                        text="30 LP: compulsory module Computational Sciences (15 LP) plus 15 LP chosen by bachelor background.",
                        minimum=30,
                        maximum=30,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Bereich Scientific Computing",
                        text="30 LP: two thematically different 15-LP modules, one from Angebot A and one from Angebot B.",
                        minimum=30,
                        maximum=30,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Spezialisierungsbereich",
                        text="30 LP in one of Molecular Sciences, Geosciences, or Atmospheric Sciences.",
                        minimum=30,
                        maximum=30,
                        unit="LP",
                    ),
                    ProgramRuleItem(label="Masterarbeit", text="Masterarbeit with accompanying colloquium, 30 LP.", minimum=30, maximum=30, unit="LP"),
                    ProgramRuleItem(label="Regelstudienzeit", text="Four semesters."),
                    ProgramRuleItem(
                        label="Language",
                        text="The modules described in the regulations are taught in English; the Masterarbeit is written and presented in English unless the Prüfungsausschuss approves another language.",
                    ),
                    ProgramRuleItem(
                        label="No repeats from the bachelor's degree",
                        text=(
                            "Modules chosen in the Synchronisierung, Scientific Computing, and specialisation areas must not match "
                            "modules already completed in the bachelor's degree. In doubt the Prüfungsausschuss decides; clarify "
                            "this before taking the module (§ 7(7))."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Graded LP",
                        text=(
                            "The certificate counts 15 of the 30 Synchronisierung LP, 15 of the 30 Scientific Computing LP, all "
                            "30 specialisation LP, and the 30-LP Masterarbeit as graded LP that affect the final grade. The A "
                            "variants of the Scientific Computing modules are not graded (pass/fail); the B variants are graded."
                        ),
                    ),
                ],
                sources=[STUDY_REGULATIONS, AMENDMENT_2026],
            ),
            ProgramRuleSection(
                id="synchronisation",
                title="Synchronisierungsbereich",
                description=(
                    "Complements each student's profile depending on their bachelor's subject (§ 7(2)). Computational "
                    "Sciences (15 LP) is compulsory; the other 15 LP depend on the bachelor background."
                ),
                items=[
                    ProgramRuleItem(label="Synchronisierung volume", text="30 LP in total.", minimum=30, maximum=30, unit="LP"),
                    ProgramRuleItem(
                        label="Computational Sciences (compulsory)",
                        text=(
                            "15 LP, every winter semester, one or two semesters: lecture and project seminar on one to three "
                            "interdisciplinary problems (theory, algorithms, numerics, efficiency); team implementation; written "
                            "exam (120 minutes)."
                        ),
                        minimum=15,
                        maximum=15,
                        unit="LP",
                    ),
                    *[
                        ProgramRuleItem(label=f"Background: {background}", text=choice)
                        for background, choice in SYNC_BY_BACKGROUND
                    ],
                    *[
                        ProgramRuleItem(label=f"Offer: {subject}", text=f"{modules}.")
                        for subject, modules in SYNC_OFFERS
                    ],
                    ProgramRuleItem(
                        label="Modules from other programmes",
                        text=(
                            "Chemistry, geology, geography, and meteorology Synchronisierung modules follow the regulations of "
                            "their home programmes (e.g. B.Sc. Chemie, B.Sc. Meteorologie, M.Sc. Planetary Sciences and Space "
                            "Exploration)."
                        ),
                    ),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="scientific-computing",
                title="Bereich Scientific Computing",
                description=(
                    "Choose two thematically different 15-LP modules (30 LP): one from Angebot A and one from Angebot B "
                    "(§ 7(3)). Each topic exists as an A variant (ungraded) and a B variant (graded)."
                ),
                items=[
                    ProgramRuleItem(label="Scientific Computing volume", text="Two modules of 15 LP each.", minimum=30, maximum=30, unit="LP"),
                    ProgramRuleItem(label="Informatik (A and B)", text=_variants(SC_INFORMATIK)),
                    ProgramRuleItem(label="Numerik (A and B)", text=_variants(SC_NUMERIK)),
                    ProgramRuleItem(label="Statistik (A and B)", text=_variants(SC_STATISTIK)),
                    ProgramRuleItem(
                        label="No same topic twice",
                        text=(
                            "The two modules must cover different topics. A topic already completed as an A variant in the "
                            "Synchronisierungsbereich cannot be taken again as its B variant here."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Grading",
                        text="A-variant modules are not graded (pass/fail); B-variant modules are graded.",
                    ),
                    ProgramRuleItem(label="Offering", text="All Scientific Computing modules are offered at least once per academic year."),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="specialisation-molecular-sciences",
                title="Specialisation: Molecular Sciences",
                description="One specialisation area of 30 LP is chosen (§ 7(4) Nr. 1). Molecular Sciences combines four offers.",
                items=[
                    ProgramRuleItem(label="Specialisation volume", text="30 LP in total.", minimum=30, maximum=30, unit="LP"),
                    ProgramRuleItem(
                        label="Angebot A (5-10 LP)",
                        text="Foundations of Molecular Simulation (5 LP), Advanced Molecular Simulation (5 LP, irregular), or Advanced Computational Physics (10 LP).",
                        minimum=5,
                        maximum=10,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Angebot B (5-10 LP)",
                        text="One or two of Dichtefunktionaltheorie (5 LP) and Quantenchemie (5 LP).",
                        minimum=5,
                        maximum=10,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Angebot C (5-10 LP)",
                        text="One of Scientific Project A (5 LP) or Scientific Project E (10 LP).",
                        minimum=5,
                        maximum=10,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Angebot D (0-15 LP)",
                        text=(
                            "Up to 15 LP from Markov Modeling (5 LP, irregular), Quantenchemische Korrelationsmethoden (5 LP), "
                            "Quantenreaktionsdynamik (5 LP), Elektronenstrukturmethoden (5 LP), Quantum Information Theory "
                            f"(10 LP), {SPECIALISATION_ELECTIVES}."
                        ),
                        minimum=0,
                        maximum=15,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Modules from other programmes",
                        text=(
                            "Advanced Computational Physics and Quantum Information Theory follow the M.Sc. Physik regulations; "
                            "the quantum-chemistry modules follow the M.Sc. Chemie regulations."
                        ),
                    ),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="specialisation-geosciences",
                title="Specialisation: Geosciences",
                description="Geosciences specialisation of 30 LP (§ 7(4) Nr. 2).",
                items=[
                    ProgramRuleItem(label="Specialisation volume", text="30 LP in total.", minimum=30, maximum=30, unit="LP"),
                    ProgramRuleItem(
                        label="Angebot A (6-12 LP)",
                        text="One or two of MSc-GP002 Physik der Erde I: Physik der Erde (6 LP) and MSc-GP006 Seismik II: Theorie seismischer Wellen (6 LP).",
                        minimum=6,
                        maximum=12,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Angebot B (6-12 LP)",
                        text=(
                            "One or two of MSc-GP003 Physik der Erde II: Eiszeiten als geodynamisches Werkzeug (6 LP) and "
                            "MSc-GP007 Seismik III: Inversions- und Abbildungsverfahren in der Geophysik (6 LP)."
                        ),
                        minimum=6,
                        maximum=12,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Angebot C (6-7 LP)",
                        text="One of Scientific Project B (6 LP) or Scientific Project C (7 LP).",
                        minimum=6,
                        maximum=7,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Angebot D (0-12 LP)",
                        text=(
                            "Up to 12 LP from MSc-GG006 Dynamik der Erde (6 LP), MSc-GG002 Thermodynamik und Kinetik von "
                            "geologischen Prozessen (6 LP), Geophysical modelling of planets and moons (5 LP), "
                            f"{SPECIALISATION_ELECTIVES}."
                        ),
                        minimum=0,
                        maximum=12,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Modules from other programmes",
                        text=(
                            "The MSc-GP/GG modules follow the M.Sc. Geologische Wissenschaften regulations; Geophysical modelling "
                            "of planets and moons follows the M.Sc. Planetary Sciences and Space Exploration regulations."
                        ),
                    ),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="specialisation-atmospheric-sciences",
                title="Specialisation: Atmospheric Sciences",
                description="Atmospheric Sciences specialisation of 30 LP (§ 7(4) Nr. 3).",
                items=[
                    ProgramRuleItem(label="Specialisation volume", text="30 LP in total.", minimum=30, maximum=30, unit="LP"),
                    ProgramRuleItem(
                        label="Angebot A (8-16 LP)",
                        text="One or two of Wetter- und Klimadiagnose (8 LP), Klimavariabilität und -modelle (8 LP), and Modelle für Wetter und Umwelt (8 LP).",
                        minimum=8,
                        maximum=16,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Angebot B (6-9 LP)",
                        text="One of Scientific Project B (6 LP) or Scientific Project D (9 LP).",
                        minimum=6,
                        maximum=9,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Angebot C (5-16 LP)",
                        text=(
                            "Satellitenmeteorologie (8 LP), Theoretische Meteorologie I (8 LP), Theoretische Meteorologie II "
                            f"(8 LP), {SPECIALISATION_ELECTIVES}."
                        ),
                        minimum=5,
                        maximum=16,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Inconsistencies in the regulation",
                        text=(
                            "§ 7(4) gives Angebot C as 5-16 LP in its heading but 5-12 LP in the sentence below, and Anlage 1 "
                            "lists Wetter- und Klimadiagnose with 6 LP instead of 8 LP. Confirm with the Prüfungsausschuss "
                            "before planning around these values."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Modules from other programmes",
                        text="The meteorology modules follow the M.Sc. Meteorologie regulations.",
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
                            "On application to the Prüfungsausschuss: last enrolled in the M.Sc. Computational Sciences at FU "
                            "Berlin, all Synchronisierung modules (30 LP) completed, and at least 60 LP of master's modules in "
                            "total. Attach a supervisor's confirmation; without one the Prüfungsausschuss assigns a supervisor."
                        ),
                    ),
                    ProgramRuleItem(label="Working time", text="23 weeks for the written part, starting when the Prüfungsausschuss issues the topic."),
                    ProgramRuleItem(label="Topic return", text="The topic can be returned once within the first four weeks."),
                    ProgramRuleItem(label="Language and length", text="English (another language on application); about 20 to 80 pages depending on the specialisation."),
                    ProgramRuleItem(
                        label="Colloquium",
                        text="Active participation in a research colloquium where progress is presented is compulsory.",
                    ),
                    ProgramRuleItem(
                        label="Assessment",
                        text=(
                            "Two examiners covering the specialisation and the mathematical/computer-science foundations grade "
                            "the written part within four weeks. A graded talk of about 30 minutes with discussion takes place in "
                            "the last third of the working time. The written part counts four fifths, the talk one fifth; both "
                            "must be passed with at least 4.0."
                        ),
                    ),
                    ProgramRuleItem(
                        label="External thesis",
                        text=(
                            "On application it can be written outside the four Fachbereiche if an authorised examiner employed at "
                            "one of them agrees to assess it."
                        ),
                    ),
                    ProgramRuleItem(label="Submission", text="Electronic submission as a machine-readable PDF with a declaration of independent work."),
                ],
                sources=[STUDY_REGULATIONS, AMENDMENT_2026],
            ),
            ProgramRuleSection(
                id="study-plan",
                title="Exemplary Study Plans",
                description="Anlage 2 gives two recommended variants for the first year; the second year is the same in both.",
                items=[
                    *[ProgramRuleItem(label=f"Variant A, {semester}", text=modules) for semester, modules in STUDY_PLAN_A],
                    *[ProgramRuleItem(label=f"Variant B, {semester}", text=modules) for semester, modules in STUDY_PLAN_B[:2]],
                    ProgramRuleItem(
                        label="Advising",
                        text=(
                            "A meeting with a Prüfungsausschuss member or the programme coordination within the first two weeks "
                            "of the first semester is strongly recommended to plan the Synchronisierung, Scientific Computing, and "
                            "specialisation choices (§ 4(3))."
                        ),
                    ),
                ],
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
                            "A written exam passed with 4.0 or better may be repeated once to improve the grade in a resit held "
                            "at the latest in the first lecture week of the following semester; the better grade counts. Not "
                            "possible for repeat examinations."
                        ),
                    ),
                    ProgramRuleItem(label="Attendance", text="Where regular attendance is compulsory, at least 80% of the contact time must be attended."),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="double-degree",
                title="EUMaster4HPC Double Master",
                description=(
                    "Students selected for the Pan-European Master Programme in High Performance Computing (EUMaster4HPC) "
                    "study in a double master's programme; it applies from WiSe 2026/27 (§ 8, added by the 2026 amendment)."
                ),
                items=[
                    ProgramRuleItem(
                        label="Structure",
                        text=(
                            "120 LP: the first year (60 LP) at FU Berlin with the Synchronisierungsbereich and the Scientific "
                            "Computing area; the second year (60 LP) at a partner university with the specialisation (30 LP) and "
                            "the Masterarbeit (30 LP) under the partner's rules and deadlines."
                        ),
                    ),
                    ProgramRuleItem(label="Learning agreement", text="A learning agreement is mandatory before the studies start."),
                    ProgramRuleItem(
                        label="Partner universities",
                        text=(
                            "Grade conversion tables exist for the University of Luxembourg, Universitat Politècnica de "
                            "Catalunya, Sorbonne Université, Politecnico di Milano, Sofia University, VSB Technical University "
                            "of Ostrava, and AGH University of Krakow."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Degree",
                        text="M.Sc. with certificates from both FU Berlin and the partner university; grades from the partner are converted with the official tables.",
                    ),
                ],
                sources=[AMENDMENT_2026],
            ),
            ProgramRuleSection(
                id="admission",
                title="Admission Requirements",
                description="Access requirements and selection from the 2020 Zugangssatzung.",
                items=[
                    ProgramRuleItem(
                        label="Eligible bachelor's degrees",
                        text=(
                            "A bachelor's degree (or equivalent) in Chemie with at least 10 LP mathematics and 8 LP physics; "
                            "Physik; Geologische Wissenschaften; Meteorologie or Geographische Wissenschaften with at least 10 LP "
                            "mathematics; Mathematik with at least 20 LP in computer science, chemistry, and/or physics; "
                            "Informatik or an engineering degree with at least 20 LP in mathematics, chemistry, and/or physics."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Language",
                        text="English at CEFR level B1 unless the degree was taught in English; no German certificate is required.",
                    ),
                    ProgramRuleItem(label="Application deadline", text="31 May each year, through the FU online application."),
                    ProgramRuleItem(
                        label="Selection",
                        text=(
                            "Up to 50 points for the final grade plus 15 points for at least 10 extra LP in mathematics or "
                            "computer science (natural-science applicants) or in a relevant natural science (mathematics or "
                            "computer-science applicants); 65 points maximum."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Applying before graduation",
                        text=(
                            "Possible with a transcript when at least two thirds of the degree are graded and the thesis is "
                            "registered; admission is then provisional until the degree certificate is submitted."
                        ),
                    ),
                ],
                sources=[ADMISSION_REGULATIONS],
            ),
            ProgramRuleSection(
                id="advising-and-abroad",
                title="Advising, Study Abroad, and Transition",
                description="Advising, study abroad, and the transition from the 2016 regulations (§§ 4, 14, 16).",
                items=[
                    ProgramRuleItem(
                        label="Study advising",
                        text=(
                            "Studienfachberatung is given by the lecturers of the programme in their office hours, plus at least "
                            "one student advisor. Students who earned less than a third of the expected LP are offered advising "
                            "after half of the Regelstudienzeit at the latest."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Study abroad",
                        text=(
                            "Recommended in the second or third semester, based on a learning agreement with the Prüfungsausschuss "
                            "chair; the programme coordination helps with planning and funding."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Transition from the 2016 regulations",
                        text=(
                            "Students enrolled before WiSe 2025/26 continue under the 2016 regulations (FU-Mitteilungen 13/2016) "
                            "unless they apply to switch (irrevocable). Graduating under the 2016 regulations is possible until "
                            "the end of SoSe 2028. This catalogue covers only the 2025 regulations."
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
                    "Humboldt-Universität or Technische Universität Berlin can only count through recognition by the "
                    "Prüfungsausschuss Computational Sciences."
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
                            "The degree has no free elective area, so an external module must be recognised as equivalent to a "
                            "listed module. Clarify this with the Prüfungsausschuss beforehand, then apply for recognition with "
                            "the Leistungsnachweis and the module description."
                        ),
                    ),
                    ProgramRuleItem(label="No double counting", text="Modules must not match modules already taken in the bachelor's degree, and the same content counts only once."),
                ],
                sources=CROSS_UNIVERSITY_SOURCES,
            ),
        ],
    )
