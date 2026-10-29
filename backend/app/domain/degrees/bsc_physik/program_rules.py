from functools import lru_cache

from app.domain.program_rules import (
    CROSS_UNIVERSITY_RULE_SECTION_ID,
    ProgramRuleItem,
    ProgramRuleSection,
    ProgramRuleSource,
    ProgramRulesCatalogue,
)


STUDY_REGULATIONS = ProgramRuleSource(
    label="B.Sc. Physik Studien- und Pruefungsordnung 2024 (FU-Mitteilungen 12/2024, pp. 484-507)",
    path="https://www.fu-berlin.de/service/zuvdocs/amtsblatt/2024/ab122024.pdf",
)
ABV_REGULATIONS = ProgramRuleSource(
    label="Allgemeine ABV Studien- und Pruefungsordnung 2023 (FU-Mitteilungen 33/2023)",
    path="https://www.fu-berlin.de/service/zuvdocs/amtsblatt/2023/ab332023.pdf",
)
ABV_AMENDMENT = ProgramRuleSource(
    label="ABV amendment 2025 (FU-Mitteilungen 05/2025)",
    path="https://www.fu-berlin.de/service/zuvdocs/amtsblatt/2025/ab052025.pdf",
)
DEPARTMENT_PAGE = ProgramRuleSource(
    label="Fachbereich Physik - Bachelorstudium",
    path="https://www.physik.fu-berlin.de/studium/bachelor/index.html",
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

# (name, LP, offering frequency and duration, assessment) per Anlage 1.
COMPULSORY_MODULES = (
    ("Einführung in die Physik", 15, "every WiSe, one semester", "no module examination (ungraded)"),
    ("Elektrodynamik und Optik", 8, "every SoSe, one semester", "graded module examination"),
    ("Grundlagen der Mess- und Labortechnik", 16, "two semesters, starting in SoSe", "graded module examination; compulsory attendance in both internal Praktika"),
    ("Struktur der Materie", 16, "at least once per academic year", "oral examination (about 45 minutes)"),
    ("Methodenpraktikum", 6, "every semester, one semester", "graded module examination; compulsory attendance"),
    ("Analytische Mechanik", 8, "every SoSe, one semester", "graded module examination"),
    ("Quantenmechanik", 12, "every WiSe, one semester", "graded module examination"),
    ("Theoretische Elektrodynamik", 8, "every SoSe, one semester", "graded module examination"),
    ("Lineare Algebra", 8, "every WiSe, one semester", "written exam (90 minutes)"),
    ("Analysis", 16, "two semesters: Vorlesung 1 in SoSe, Vorlesung 2 in WiSe", "written exam (90 minutes)"),
)

COMPULSORY_ELECTIVE_MODULES = (
    ("Biophysik", 10, "once per academic year"),
    ("Astronomie und Astrophysik", 10, "once per academic year"),
    ("Kern- und Elementarteilchenphysik", 10, "once per academic year"),
    ("Computerphysik", 10, "once per academic year"),
    ("Ausgewählte Kapitel der Physik", 5, "irregular; seminar with a talk (about 30 minutes) and compulsory attendance"),
    ("Spezielle Themen der Physik A", 5, "irregular"),
    ("Spezielle Themen der Physik B", 10, "irregular"),
)

STUDY_PLAN = (
    ("1st semester", "Einführung in die Physik, Lineare Algebra, ABV module (5 LP)"),
    ("2nd semester", "Analytische Mechanik, Elektrodynamik und Optik, Grundlagen der Mess- und Labortechnik (starts), Analysis (starts)"),
    ("3rd semester", "Quantenmechanik, Grundlagen der Mess- und Labortechnik (continued), Analysis (continued), ABV module (5 LP)"),
    ("4th semester", "Theoretische Elektrodynamik, Struktur der Materie, Projektpraktikum"),
    ("5th semester", "Struktur der Materie (continued), Methodenpraktikum, Wahlpflicht (15 LP), Berufspraktikum (10 LP)"),
    ("6th semester", "Bachelorarbeit, Wahlpflicht (10 LP), Präsentationstechniken"),
)


@lru_cache(maxsize=1)
def get_program_rules() -> ProgramRulesCatalogue:
    return ProgramRulesCatalogue(
        degree_program="FU Berlin B.Sc. Physik",
        regulation="2024 study and examination regulations (FU-Mitteilungen 12/2024)",
        catalogue_version="bsc-physik-2024-v1",
        source_note=(
            "Rules catalogue for the FU Berlin B.Sc. Physik (Monobachelor) under the 2024 "
            "regulations, which apply to students enrolled after they came into force. "
            "Official FU documents and the Prüfungsausschuss Physik remain authoritative."
        ),
        sections=[
            ProgramRuleSection(
                id="overall-structure",
                title="Overall Structure",
                description=(
                    "The degree comprises 180 LP over a standard duration of six semesters: "
                    "the Kernfach Physik (150 LP including the 12-LP Bachelorarbeit) plus "
                    "30 LP Allgemeine Berufsvorbereitung (ABV)."
                ),
                items=[
                    ProgramRuleItem(label="Total degree volume", text="180 LP total.", minimum=180, maximum=180, unit="LP"),
                    ProgramRuleItem(label="Kernfach Physik", text="150 LP, including the Bachelorarbeit (12 LP).", minimum=150, maximum=150, unit="LP"),
                    ProgramRuleItem(label="ABV", text="30 LP Allgemeine Berufsvorbereitung.", minimum=30, maximum=30, unit="LP"),
                    ProgramRuleItem(label="Regelstudienzeit", text="Six semesters."),
                    ProgramRuleItem(
                        label="Grading",
                        text=(
                            "135 of the 150 Kernfach LP are graded and count toward the final grade; "
                            "Einführung in die Physik (15 LP) has no module examination. ABV is "
                            "ungraded (bestanden / nicht bestanden)."
                        ),
                    ),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="kernfach-structure",
                title="Kernfach Physik",
                description="The 150-LP Kernfach is divided into a Pflichtbereich and a Wahlpflichtbereich (§ 7).",
                items=[
                    ProgramRuleItem(label="Pflichtbereich", text="125 LP: the listed compulsory modules (113 LP) plus the Bachelorarbeit (12 LP).", minimum=125, maximum=125, unit="LP"),
                    ProgramRuleItem(label="Wahlpflichtbereich", text="25 LP of compulsory-elective modules.", minimum=25, maximum=25, unit="LP"),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="compulsory-modules",
                title="Compulsory Modules",
                description="All of these modules are mandatory and together total 113 LP.",
                items=[
                    ProgramRuleItem(
                        label=name,
                        text=f"{lp} LP, offered {frequency}; {assessment}.",
                        minimum=lp,
                        maximum=lp,
                        unit="LP",
                    )
                    for name, lp, frequency, assessment in COMPULSORY_MODULES
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="compulsory-elective-modules",
                title="Compulsory-Elective Modules (Wahlpflichtbereich)",
                description=(
                    "Choose modules totalling 25 LP. The Fachbereich Physik offers the modules below; "
                    "modules from other Fachbereiche are also possible."
                ),
                items=[
                    ProgramRuleItem(label="Wahlpflicht volume", text="Modules totalling exactly 25 LP.", minimum=25, maximum=25, unit="LP"),
                    *[
                        ProgramRuleItem(label=name, text=f"{lp} LP, offered {frequency}.", minimum=lp, maximum=lp, unit="LP")
                        for name, lp, frequency in COMPULSORY_ELECTIVE_MODULES
                    ],
                    ProgramRuleItem(
                        label="Modules from other Fachbereiche",
                        text=(
                            "Modules from the core areas of the FU bachelor programmes Betriebswirtschaftslehre, "
                            "Biochemie, Bioinformatik, Biologie, Chemie, Geologische Wissenschaften, Informatik, "
                            "Mathematik, Meteorologie, Philosophie, and Volkswirtschaftslehre can be chosen, "
                            "provided access can be granted. The Prüfungsausschuss publishes a list of recommendations."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Further modules on application",
                        text=(
                            "On application to the Prüfungsausschuss, other suitable modules at FU Berlin or at "
                            "other universities can be taken; the Prüfungsausschuss decides."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Recommendation",
                        text="Modules on sustainability, gender, and diversity topics are recommended for consideration.",
                    ),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="abv",
                title="Allgemeine Berufsvorbereitung (ABV)",
                description=(
                    "The 30-LP ABV area comprises the two Physik-specific modules, freely chosen ABV "
                    "competence modules, and a compulsory Berufspraktikum (§ 9)."
                ),
                items=[
                    ProgramRuleItem(label="ABV total", text="30 LP in total.", minimum=30, maximum=30, unit="LP"),
                    ProgramRuleItem(
                        label="Fachnahe Zusatzqualifikationen",
                        text=(
                            "Projektpraktikum (5 LP, every semester, no module examination, compulsory attendance) "
                            "and Präsentationstechniken (5 LP, every semester, talk of about 30 minutes, compulsory "
                            "attendance), 10 LP together."
                        ),
                        minimum=10,
                        maximum=10,
                        unit="LP",
                    ),
                    ProgramRuleItem(label="Free ABV modules", text="Freely chosen modules in ABV competence areas worth 5, 10, or 15 LP."),
                    ProgramRuleItem(
                        label="Berufspraktikum",
                        text=(
                            "A Berufspraktikum of 5, 10, or 15 LP is compulsory; 10 LP is recommended. The "
                            "Praktikumsbeauftragte of the Fachbereich Physik advises on internships and should be "
                            "consulted about the chosen host institution."
                        ),
                    ),
                    ProgramRuleItem(label="No content overlap", text="ABV modules must not match modules or work of the Kernfach."),
                ],
                sources=[STUDY_REGULATIONS, ABV_REGULATIONS, ABV_AMENDMENT],
            ),
            ProgramRuleSection(
                id="study-plan",
                title="Exemplary Study Plan",
                description="Recommended (not binding) sequence from Anlage 2 of the regulations.",
                items=[ProgramRuleItem(label=semester, text=modules) for semester, modules in STUDY_PLAN],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="bachelorarbeit",
                title="Bachelorarbeit",
                description="The Bachelorarbeit counts as 12 LP within the Pflichtbereich (§ 10).",
                items=[
                    ProgramRuleItem(
                        label="Admission",
                        text=(
                            "Last enrolled in the B.Sc. Physik at FU Berlin, and Struktur der Materie (16 LP) plus "
                            "seven further compulsory modules of § 7(3) successfully completed. A confirmation from "
                            "an examiner willing to supervise must be attached to the application."
                        ),
                    ),
                    ProgramRuleItem(label="Workload and deadline", text="360 hours of work; submission deadline 24 weeks after the topic is issued."),
                    ProgramRuleItem(label="Expected length", text="Approximately 7,500 words."),
                    ProgramRuleItem(label="Language", text="German or English; another language requires approval by the Prüfungsausschuss."),
                    ProgramRuleItem(label="Topic return", text="The topic can be returned once within the first three weeks."),
                    ProgramRuleItem(label="Submission", text="Electronic submission as a machine-readable PDF with a declaration of independent work."),
                    ProgramRuleItem(label="Assessment", text="Two examiners grade it within four weeks; it is passed with at least grade 4.0."),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="examinations",
                title="Examinations and Repetition",
                description="Rules on repeating examinations and grade improvement (§ 13).",
                items=[
                    ProgramRuleItem(label="Failed examinations", text="A failed Bachelorarbeit may be repeated twice; other examinations may be repeated three times."),
                    ProgramRuleItem(
                        label="Grade improvement",
                        text=(
                            "A written exam passed with 4.0 or better may be repeated once to improve the grade, at the "
                            "latest in the first lecture week of the following semester; the better grade counts. Not "
                            "possible for repeat examinations."
                        ),
                    ),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="advising-and-abroad",
                title="Advising, Study Abroad, and Transition",
                description="Advising, recommended study-abroad window, and the transition from the 2012 regulations (§§ 4, 14, 16).",
                items=[
                    ProgramRuleItem(
                        label="Study advising",
                        text=(
                            "Students who have earned less than one third of the expected LP after half of the "
                            "Regelstudienzeit are offered Studienfachberatung."
                        ),
                    ),
                    ProgramRuleItem(label="Study abroad", text="Recommended in the fifth semester, based on a learning agreement with the Prüfungsausschuss chair."),
                    ProgramRuleItem(
                        label="Transition from the 2012 regulations",
                        text=(
                            "Students enrolled before these regulations came into force continue under the 2012 "
                            "Studien- and Prüfungsordnung unless they apply to switch (irrevocable). Graduating "
                            "under the 2012 regulations is possible until the end of SoSe 2027."
                        ),
                    ),
                ],
                sources=[STUDY_REGULATIONS, DEPARTMENT_PAGE],
            ),
            ProgramRuleSection(
                id=CROSS_UNIVERSITY_RULE_SECTION_ID,
                title="Courses at HU Berlin and TU Berlin (Nebenhörerschaft)",
                description=(
                    "Modules taken as a cross-registered student ('Nebenhörer', also called "
                    "Zweithörerschaft) at Humboldt-Universität or Technische Universität Berlin can be "
                    "recognized on application to the Prüfungsausschuss Physik."
                ),
                items=[
                    ProgramRuleItem(
                        label="Legal basis",
                        text=(
                            "Berlin's universities allow students to attend and be examined in individual courses at "
                            "a partner university as a Nebenhörer; § 7(4) allows suitable modules at other "
                            "universities in the Wahlpflichtbereich on application to the Prüfungsausschuss."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Enrollment as Nebenhörer",
                        text=(
                            "Ask the teacher of the HU/TU course for approval and submit the Nebenhörer application "
                            "described on the [HU Nebenhörerschaft page](https://www.hu-berlin.de/studium/nach-dem-studium/lebenslanges-lernen/gasthoerer-und-nebenhoererschaft) "
                            "or the [TU Nebenhörerschaft page](https://www.tu.berlin/studierendensekretariat/themen-a-z/gast-und-nebenhoererschaft/)."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Recognition at FU",
                        text=(
                            "Apply to the Prüfungsausschuss Physik for recognition with the Leistungsnachweis and the "
                            "module description; clarify beforehand whether and how the module can count."
                        ),
                    ),
                    ProgramRuleItem(label="No double counting", text="The same content can only be counted once in the degree."),
                ],
                sources=CROSS_UNIVERSITY_SOURCES,
            ),
        ],
    )
