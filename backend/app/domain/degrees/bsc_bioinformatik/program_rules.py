from functools import lru_cache

from app.domain.program_rules import (
    CROSS_UNIVERSITY_RULE_SECTION_ID,
    ProgramRuleItem,
    ProgramRuleSection,
    ProgramRuleSource,
    ProgramRulesCatalogue,
)


STUDY_REGULATIONS = ProgramRuleSource(
    label="B.Sc. Bioinformatik Studien- und Pruefungsordnung 2023 (FU-Mitteilungen 34/2023, pp. 1218-1243)",
    path="https://www.fu-berlin.de/service/zuvdocs/amtsblatt/2023/ab342023.pdf",
)
ABV_REGULATIONS = ProgramRuleSource(
    label="Allgemeine ABV Studien- und Pruefungsordnung 2023 (FU-Mitteilungen 33/2023)",
    path="https://www.fu-berlin.de/service/zuvdocs/amtsblatt/2023/ab332023.pdf",
)
ABV_AMENDMENT = ProgramRuleSource(
    label="ABV amendment 2025 (FU-Mitteilungen 05/2025)",
    path="https://www.fu-berlin.de/service/zuvdocs/amtsblatt/2025/ab052025.pdf",
)
PROGRAM_PAGE = ProgramRuleSource(
    label="Bioinformatik - Bachelor: Profil und Aufbau",
    path="https://www.mi.fu-berlin.de/bioinf/stud/bachelor/profil_aufbau2023/index.html",
)
WAHLBEREICH_PAGE = ProgramRuleSource(
    label="Bioinformatik - Bachelor: Wahlbereich",
    path="https://www.mi.fu-berlin.de/bioinf/stud/bachelor/wahlbereich/index.html",
)
ABV_PAGE = ProgramRuleSource(
    label="Bioinformatik - Bachelor: ABV",
    path="https://www.mi.fu-berlin.de/bioinf/stud/bachelor/abv/index.html",
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
    WAHLBEREICH_PAGE,
]

# (name, LP, offering, teaching and assessment) per § 7 and Anlage 1.
INFORMATIK_MODULES = (
    ("Konzepte der Programmierung", 9, "as in the B.Sc. Informatik", "shared with the B.Sc. Informatik; its regulation applies"),
    ("Algorithmen und Datenstrukturen", 9, "as in the B.Sc. Informatik", "shared with the B.Sc. Informatik; its regulation applies"),
    ("Algorithmische Bioinformatik I und Numerik", 5, "every WiSe", "lecture with Übung; written exam (90 minutes)"),
    ("Praxis der Algorithmischen Bioinformatik I und Numerik", 5, "every WiSe", "Praktikum; ungraded oral examination (about 20 minutes)"),
    ("Algorithmische Bioinformatik II", 6, "every SoSe", "lecture with Übung; written exam (90 minutes)"),
    ("Algorithmische Bioinformatik III und Statistik", 7, "every WiSe", "lecture with Übung and seminar-style teaching; written exam (90 minutes)"),
    ("Wissenschaftliches Arbeiten in der Bioinformatik", 5, "starts in WiSe, two semesters", "lecture plus seminar, partly at the Charité; no module examination (ungraded)"),
)

MATHEMATIK_MODULES = (
    ("Diskrete Strukturen für Informatik", 9, "as in the B.Sc. Informatik", "shared with the B.Sc. Informatik; its regulation applies"),
    ("Lineare Algebra für Informatik", 9, "as in the B.Sc. Informatik", "shared with the B.Sc. Informatik; its regulation applies"),
    ("Analysis für Informatik", 9, "as in the B.Sc. Informatik", "shared with the B.Sc. Informatik; its regulation applies"),
    ("Statistik für Bioinformatik I", 6, "every SoSe", "lecture with Übung at the Charité; written exam (90 minutes)"),
    ("Statistik für Bioinformatik II und Maschinelles Lernen", 6, "every WiSe", "lecture with Übung at the Charité; written exam (90 minutes)"),
)

BIOLOGIE_CHEMIE_MODULES = (
    ("Allgemeine Chemie", 7, "every WiSe", "lecture plus laboratory course; practical examination"),
    ("Allgemeine Biologie", 5, "every WiSe", "lectures (botany and zoology parts); no module examination (ungraded)"),
    ("Molekularbiologie und Biochemie I", 6, "every SoSe per the regulation (WiSe 26/27: the VV lists Biochemie I as the equivalent)", "lecture with Übung; written exam (90 minutes)"),
    ("Molekularbiologie und Biochemie II", 6, "every WiSe", "lecture with Übung; written exam; requires Molekularbiologie und Biochemie I"),
    ("Molekularbiologie und Biochemie III", 6, "every SoSe", "lecture with Übung; written exam; requires Molekularbiologie und Biochemie I"),
    ("Genetik und Genomforschung", 5, "every WiSe", "lecture with Übung; written exam; requires Molekularbiologie und Biochemie II"),
    ("Medizinische Physiologie", 7, "every SoSe", "lecture, seminar and laboratory course at the Charité; written exam"),
    ("Neurobiologie", 5, "every WiSe", "lecture plus laboratory course; written exam"),
)

STUDY_PLAN = (
    ("1st semester (30 LP)", "Konzepte der Programmierung, Diskrete Strukturen für Informatik, Allgemeine Biologie, Allgemeine Chemie"),
    ("2nd semester (31 LP)", "Algorithmen und Datenstrukturen, Lineare Algebra für Informatik, Medizinische Physiologie, Molekularbiologie und Biochemie I"),
    ("3rd semester (30 LP)", "Algorithmische Bioinformatik I und Numerik, Praxis der Algorithmischen Bioinformatik I und Numerik, Analysis für Informatik, Molekularbiologie und Biochemie II, ABV (5 LP)"),
    ("4th semester (30 LP)", "Wahlbereich (6 LP), Algorithmische Bioinformatik II, Statistik für Bioinformatik I, Molekularbiologie und Biochemie III; Berufspraktikum (10 LP) in the break after the 4th semester"),
    ("5th semester (30 LP)", "Wissenschaftliches Arbeiten in der Bioinformatik (starts, continues in the 6th), Algorithmische Bioinformatik III und Statistik, Statistik für Bioinformatik II und Maschinelles Lernen, Neurobiologie, Genetik und Genomforschung"),
    ("6th semester (29 LP)", "Bachelorarbeit, Projektmanagement im Softwarebereich (March to May), ABV (5 LP)"),
)


def _module_items(modules: tuple[tuple[str, int, str, str], ...]) -> list[ProgramRuleItem]:
    return [
        ProgramRuleItem(
            label=name,
            text=f"{lp} LP, offered {frequency}; {assessment}.",
            minimum=lp,
            maximum=lp,
            unit="LP",
        )
        for name, lp, frequency, assessment in modules
    ]


@lru_cache(maxsize=1)
def get_program_rules() -> ProgramRulesCatalogue:
    return ProgramRulesCatalogue(
        degree_program="FU Berlin B.Sc. Bioinformatik",
        regulation="2023 study and examination regulations (FU-Mitteilungen 34/2023)",
        catalogue_version="bsc-bioinformatik-2023-v1",
        source_note=(
            "Rules catalogue for the FU Berlin B.Sc. Bioinformatik, a joint programme of the FU "
            "Fachbereiche Mathematik und Informatik and Biologie, Chemie, Pharmazie with the Charité, "
            "under the 2023 regulations. Official FU documents and the Prüfungsausschuss remain "
            "authoritative."
        ),
        sections=[
            ProgramRuleSection(
                id="overall-structure",
                title="Overall Structure",
                description=(
                    "The degree comprises 180 LP over a standard duration of six semesters: the "
                    "Kernfach Bioinformatik (150 LP including the 12-LP Bachelorarbeit) plus 30 LP "
                    "Allgemeine Berufsvorbereitung (ABV) (§ 7)."
                ),
                items=[
                    ProgramRuleItem(label="Total degree volume", text="180 LP total.", minimum=180, maximum=180, unit="LP"),
                    ProgramRuleItem(label="Kernfach Bioinformatik", text="150 LP, including the Bachelorarbeit with oral presentation (12 LP).", minimum=150, maximum=150, unit="LP"),
                    ProgramRuleItem(label="ABV", text="30 LP Allgemeine Berufsvorbereitung.", minimum=30, maximum=30, unit="LP"),
                    ProgramRuleItem(label="Regelstudienzeit", text="Six semesters."),
                    ProgramRuleItem(
                        label="Joint programme",
                        text=(
                            "Run jointly by FU Berlin and the Charité; some modules (for example Statistik "
                            "für Bioinformatik, Medizinische Physiologie) are taught at the Charité."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Ungraded parts",
                        text=(
                            "Allgemeine Biologie and Wissenschaftliches Arbeiten in der Bioinformatik have no "
                            "module examination, Praxis der Algorithmischen Bioinformatik I und Numerik is "
                            "ungraded, the thesis presentation is ungraded, and ABV is ungraded."
                        ),
                    ),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="kernfach-structure",
                title="Kernfach Bioinformatik",
                description=(
                    "Besides the 12-LP Bachelorarbeit, the Kernfach has a 132-LP Pflichtbereich in three "
                    "study areas and a 6-LP Wahlbereich (§ 7(2))."
                ),
                items=[
                    ProgramRuleItem(label="Informatik/Algorithmische Bioinformatik", text="46 LP of compulsory modules.", minimum=46, maximum=46, unit="LP"),
                    ProgramRuleItem(label="Mathematik/Statistik", text="39 LP of compulsory modules.", minimum=39, maximum=39, unit="LP"),
                    ProgramRuleItem(label="Biologie/Chemie/Biochemie", text="47 LP of compulsory modules.", minimum=47, maximum=47, unit="LP"),
                    ProgramRuleItem(label="Wahlbereich", text="6 LP of elective modules.", minimum=6, maximum=6, unit="LP"),
                    ProgramRuleItem(label="Bachelorarbeit", text="12 LP including the oral presentation.", minimum=12, maximum=12, unit="LP"),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="informatik-modules",
                title="Informatik/Algorithmische Bioinformatik (46 LP)",
                description="All of these modules are compulsory (§ 7(3)).",
                items=_module_items(INFORMATIK_MODULES),
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="mathematik-statistik-modules",
                title="Mathematik/Statistik (39 LP)",
                description="All of these modules are compulsory (§ 7(4)).",
                items=_module_items(MATHEMATIK_MODULES),
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="biologie-chemie-modules",
                title="Biologie/Chemie/Biochemie (47 LP)",
                description="All of these modules are compulsory (§ 7(5)).",
                items=_module_items(BIOLOGIE_CHEMIE_MODULES),
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="wahlbereich",
                title="Wahlbereich (6 LP)",
                description=(
                    "Deeper or complementary knowledge in one of the three study areas (§ 7(6), (7))."
                ),
                items=[
                    ProgramRuleItem(label="Volume", text="6 LP.", minimum=6, maximum=6, unit="LP"),
                    ProgramRuleItem(
                        label="Eligible modules",
                        text=(
                            "Modules from the FU bachelor programmes Informatik, Mathematik, Biochemie, and "
                            "Biologie that were not already taken in the Pflichtbereich. Modules from the "
                            "Wahlpflichtbereich of the B.Sc. Informatik are especially recommended."
                        ),
                    ),
                    ProgramRuleItem(label="No overlap", text="Wahlbereich modules must not match modules or work of the Pflichtbereich."),
                    ProgramRuleItem(
                        label="Approval",
                        text=(
                            "According to the programme page, Datenbanksysteme is recommended; other modules "
                            "need approval by the Prüfungsausschuss before the semester, with registration via "
                            "the Prüfungsbüro. There is no official list of approved modules."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Splitting",
                        text=(
                            "According to the programme page, the 6 LP can be covered by two smaller modules "
                            "(for example 2 x 5 LP)."
                        ),
                    ),
                ],
                sources=[STUDY_REGULATIONS, WAHLBEREICH_PAGE],
            ),
            ProgramRuleSection(
                id="abv",
                title="Allgemeine Berufsvorbereitung (ABV)",
                description="The 30-LP ABV area comprises three parts (§ 8(3)).",
                items=[
                    ProgramRuleItem(label="ABV total", text="30 LP in total, ungraded.", minimum=30, maximum=30, unit="LP"),
                    ProgramRuleItem(
                        label="Projektmanagement im Softwarebereich",
                        text=(
                            "10 LP from the competence area Fachnahe Zusatzqualifikationen; compulsory. Offered "
                            "as a block course in the SoSe (March to May)."
                        ),
                        minimum=10,
                        maximum=10,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Free ABV modules",
                        text="Freely chosen ABV modules totalling 10 LP, at least 5 LP of them from other competence areas than Fachnahe Zusatzqualifikationen.",
                        minimum=10,
                        maximum=10,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Berufspraktikum",
                        text=(
                            "10 LP, compulsory, at a suitable company or non-university research institution. "
                            "The placement needs approval by the Prüfungsausschuss or the internship "
                            "coordinator; it can also be done abroad. Recommended in the break after the 4th "
                            "semester."
                        ),
                        minimum=10,
                        maximum=10,
                        unit="LP",
                    ),
                    ProgramRuleItem(label="No overlap", text="ABV modules must not match modules or work of the Kernfach."),
                    ProgramRuleItem(
                        label="Programme-page notes",
                        text=(
                            "ABV should start from the 3rd semester. According to the programme page, the ZEDAT "
                            "modules on object-oriented programming and digital data analysis cannot be counted; "
                            "the C++ block course counts as a subject-related (fachnah) ABV course."
                        ),
                    ),
                ],
                sources=[STUDY_REGULATIONS, ABV_REGULATIONS, ABV_AMENDMENT, ABV_PAGE],
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
                description="The Bachelorarbeit with oral presentation counts as 12 LP (§ 10).",
                items=[
                    ProgramRuleItem(
                        label="Admission",
                        text=(
                            "At least 120 LP completed, including Diskrete Strukturen für Informatik, Lineare "
                            "Algebra für Informatik, Analysis für Informatik, Algorithmische Bioinformatik I und "
                            "Numerik, and Algorithmische Bioinformatik II; last enrolled in this programme at FU "
                            "Berlin. A supervisor's confirmation must be attached to the application."
                        ),
                    ),
                    ProgramRuleItem(label="Length and deadline", text="About 25 pages (about 7,500 words); twelve weeks."),
                    ProgramRuleItem(label="Topic return", text="The topic can be returned once within the first two weeks."),
                    ProgramRuleItem(label="Submission", text="Electronic submission as a machine-readable PDF, with source code for programs and a declaration of independent work."),
                    ProgramRuleItem(label="Assessment", text="Two examiners; the grade is the mean of both grades."),
                    ProgramRuleItem(label="Oral presentation", text="About 15 minutes talk plus about 15 minutes discussion; ungraded."),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id="examinations",
                title="Examinations, Study Abroad, and Transition",
                description="Repetition, study abroad, and the transition from the 2012 regulations (§§ 11, 12, 14).",
                items=[
                    ProgramRuleItem(label="Failed examinations", text="A failed Bachelorarbeit may be repeated twice; other examinations may be repeated three times."),
                    ProgramRuleItem(label="Study abroad", text="Recommended in the 4th semester, based on a learning agreement."),
                    ProgramRuleItem(
                        label="Transition from the 2012 regulations",
                        text=(
                            "Students enrolled before these regulations came into force continued under the 2012 "
                            "regulations unless they applied to switch (irrevocable). Graduating under the 2012 "
                            "regulations was guaranteed only until the end of SoSe 2026."
                        ),
                    ),
                ],
                sources=[STUDY_REGULATIONS],
            ),
            ProgramRuleSection(
                id=CROSS_UNIVERSITY_RULE_SECTION_ID,
                title="Courses at HU Berlin and TU Berlin (Nebenhörerschaft)",
                description=(
                    "The regulation names only FU bachelor programmes for the Wahlbereich; modules taken as "
                    "a cross-registered student ('Nebenhörer') at Humboldt-Universität or Technische "
                    "Universität Berlin need approval by the Prüfungsausschuss."
                ),
                items=[
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
                            "Clarify with the Prüfungsausschuss before the semester whether and how the module can "
                            "count; apply for recognition with the Leistungsnachweis and the module description."
                        ),
                    ),
                    ProgramRuleItem(label="No double counting", text="The same content can only be counted once in the degree."),
                ],
                sources=CROSS_UNIVERSITY_SOURCES,
            ),
        ],
    )
