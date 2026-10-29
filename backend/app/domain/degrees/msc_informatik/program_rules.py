from functools import lru_cache

from app.domain.catalog_data import course_lp, course_name, module_entries_by_id
from app.domain.program_rules import (
    ProgramRuleItem,
    ProgramRuleSection,
    ProgramRuleSource,
    ProgramRulesCatalogue,
)


DEFAULT_SOURCES = [
    ProgramRuleSource(
        label="Studien- und Prüfungsordnung 2014 (§§7, 9)",
        path="https://www.imp.fu-berlin.de/fbv/pruefungsbuero/Studien--und-Pruefungsordnungen/0089c_SPO_2014.pdf",
    ),
    ProgramRuleSource(
        label="Checkliste Master Informatik 2014",
        path="https://www.imp.fu-berlin.de/fbv/pruefungsbuero/Formulare/PDFs/Checkliste-MSc-Informatik-_2014_.pdf",
    ),
]

EXAM_BOARD_SOURCE = ProgramRuleSource(
    label="Prüfungsausschuss Informatik: Anerkennung und 15-LP-Grenze",
    path="https://www.mi.fu-berlin.de/w/Inf/PruefungsAusschuss",
    note="The 26 October 2023 decision retains the 15 LP cap even when a Bachelor exceeds 180 LP.",
)

APPLICATION_SOURCE = ProgramRuleSource(
    label="Anwendungsgebiet/Nebenfach: Zugang zu Modulen",
    path="https://www.mi.fu-berlin.de/inf/stud/nebenfachFuerInformatiker/index.html",
    note="Capacity agreements primarily concern Bachelor students; Master students have no entitlement to these places.",
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
    ProgramRuleSource(
        label="Pruefungsausschuss Informatik (Anrechnung von Leistungen)",
        path="https://www.mi.fu-berlin.de/w/Inf/PruefungsAusschuss",
    ),
]


def _checklist_slot_items() -> list[ProgramRuleItem]:
    """Expose canonical module slots without duplicating catalogue data."""
    modules = module_entries_by_id("msc_informatik").values()
    return [
        ProgramRuleItem(
            label=label,
            text="\n".join(
                f"- {course_name(module['course_id'])} ({module.get('lp', course_lp(module['course_id']))} LP)"
                for module in modules if module["area"] == area
            ),
        )
        for area, label in (
            ("practical", "Praktische Informatik module slots"),
            ("technical", "Technische Informatik module slots"),
            ("theoretical", "Theoretische Informatik module slots"),
        )
    ]


@lru_cache(maxsize=1)
def get_program_rules() -> ProgramRulesCatalogue:
    return ProgramRulesCatalogue(
        degree_program="FU Berlin Master Informatik",
        regulation="2014 Studien- und Prüfungsordnung (FU-Mitteilungen 35/2014)",
        catalogue_version="master-informatik-2014-v2",
        source_note=(
            "Overview of the official degree requirements for the FU Berlin Master Informatik "
            "(2014 study regulations). Chat plan checks are advisory and cover the implemented rules; "
            "binding recognition and eligibility decisions belong to the Prüfungsausschuss / Prüfungsbüro."
        ),
        sections=[
            ProgramRuleSection(
                id="overall-structure",
                title="Overall Structure",
                description=(
                    "120 LP in four separate parts: 70 LP Informatik + 10 LP Anwendungsbereich "
                    "+ 10 LP Wahlbereich + 30 LP Masterarbeit. Regular duration: 4 semesters."
                ),
                items=[
                    ProgramRuleItem(label="Total degree volume", text="120 LP total", minimum=120, maximum=120, unit="LP"),
                    ProgramRuleItem(
                        label="Taught modules",
                        text="70 LP Informatik, 10 LP Anwendungsbereich, and 10 LP Wahlbereich add up to exactly 90 LP; each module is allocated once.",
                        minimum=90,
                        maximum=90,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Masterarbeit",
                        text="The Masterarbeit counts as 30 LP when included in the plan.",
                        minimum=30,
                        maximum=30,
                        unit="LP",
                    ),
                    ProgramRuleItem(label="Module choice", text="Choose modules within the area, specialization, seminar, project, and grading requirements below."),
                ],
                related_issue_codes=["module_area_lp_total", "master_thesis_lp"],
                sources=DEFAULT_SOURCES,
            ),
            ProgramRuleSection(
                id="informatics-area",
                title="1. Informatik (70 LP)",
                description=(
                    "Build 70 LP in three steps: 40 LP of subject minima, 20 additional LP in one "
                    "specialization, and 10 LP freely distributed across the three Informatik subjects. "
                    "Wahlbereich is a separate 10 LP allocation."
                ),
                items=[
                    ProgramRuleItem(
                        label="Informatik total",
                        text="Exactly 70 LP, excluding every module allocated to Wahlbereich.",
                        minimum=70,
                        maximum=70,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Step 1 - Praktische Informatik",
                        text="At least 20 LP in Praktische Informatik.",
                        minimum=20,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Step 1 - Technische Informatik",
                        text="At least 10 LP in Technische Informatik.",
                        minimum=10,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Step 1 - Theoretische Informatik",
                        text="At least 10 LP in Theoretische Informatik.",
                        minimum=10,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Step 2 - Specialization (Vertiefung)",
                        text="Choose exactly one subject for 20 additional LP: at least 40 LP total in Praktische, or 30 LP total in Technische or Theoretische Informatik.",
                        minimum=20, maximum=20, unit="additional LP",
                    ),
                    ProgramRuleItem(
                        label="Step 3 - Free Informatik choice",
                        text="Distribute the remaining 10 LP freely across Praktische, Technische, and Theoretische Informatik. These 10 LP are part of Informatik, not the separate Wahlbereich.",
                        minimum=10, maximum=10, unit="LP",
                    ),
                ],
                related_issue_codes=[
                    "informatics_area_lp",
                    "specialization_missing",
                    "practical_minimum_lp",
                    "technical_minimum_lp",
                    "theoretical_minimum_lp",
                ],
                sources=DEFAULT_SOURCES,
            ),
            ProgramRuleSection(
                id="application-area",
                title="2. Anwendungsbereich (10 LP)",
                description=(
                    "10 LP from scientific subjects outside Informatik, separate from Informatik and Wahlbereich."
                ),
                items=[
                    ProgramRuleItem(
                        label="Application area LP",
                        text="Exactly 10 LP; extra modules from these subjects may be allocated to the separate Wahlbereich.",
                        minimum=10,
                        maximum=10,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Subjects and advising",
                        text="Scientific subjects outside Informatik are eligible; the SPO particularly recommends Mathematics, Bioinformatics, Physics, Philosophy, Psychology, or Chemistry. Discuss your choice, examinations, and timetable with your study adviser first (§4(5)).",
                    ),
                    ProgramRuleItem(
                        label="Access to courses",
                        text="Check prerequisites and available places with the offering department. The linked Nebenfach page mainly describes Bachelor arrangements; Master students have no entitlement to its reserved places, though remaining places may be available.",
                    ),
                ],
                related_issue_codes=["application_area_lp"],
                sources=[*DEFAULT_SOURCES, APPLICATION_SOURCE],
            ),
            ProgramRuleSection(
                id="wahlbereich",
                title="3. Wahlbereich (10 LP)",
                description=(
                    "A separate 10 LP choice from Informatik or other scientific subjects. "
                    "These credits are not added to the 70 LP Informatik or 10 LP Anwendungsbereich."
                ),
                items=[
                    ProgramRuleItem(
                        label="Wahlbereich volume",
                        text="Exactly 10 LP, explicitly allocated to Wahlbereich.",
                        minimum=10,
                        maximum=10,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Choose the subject freely",
                        text=(
                            "Choose Informatik modules or modules from scientific subjects eligible for the "
                            "Anwendungsbereich. A module retains its subject label but counts only in Wahlbereich, "
                            "not again toward subject minima or specialization."
                        ),
                    ),
                    ProgramRuleItem(label="Limits still apply", text="The overall limits of 2 Softwareprojekte, 4 seminars, 15 LP Bachelor-level modules, and the grading requirements still apply."),
                ],
                related_issue_codes=["wahlbereich_lp"],
                sources=DEFAULT_SOURCES,
            ),
            ProgramRuleSection(
                id="masterarbeit",
                title="4. Masterarbeit (30 LP)",
                description="30 LP for the thesis and presentation; admission is possible after at least 60 LP of completed Master modules (§9).",
                items=[
                    ProgramRuleItem(label="Admission", text="At least 60 LP of completed Master modules and the enrollment and supervision requirements of §9(2)-(3). The 90 LP taught-module total is not a prerequisite for starting the thesis.", minimum=60, unit="completed LP"),
                    ProgramRuleItem(label="Thesis volume", text="30 LP including presentation; it is separate from the 90 LP taught modules.", minimum=30, maximum=30, unit="LP"),
                    ProgramRuleItem(label="Written work and presentation", text="The SPO provides 23 weeks for the written part and a presentation with discussion of about 30 minutes. The written part contributes three quarters and the presentation one quarter of the thesis grade."),
                ],
                related_issue_codes=["master_thesis_lp", "wahlbereich_thesis"],
                sources=DEFAULT_SOURCES,
            ),
            ProgramRuleSection(
                id="checklist-planning",
                title="Fit Courses into the Checklist and Keep Options Open",
                description=(
                    "Plan with the checklist's module slots ('boxes'), not just course titles or LP. "
                    "Check for a dedicated named module before using a broader slot, and keep room "
                    "for courses you want to take in later semesters."
                ),
                items=[
                    ProgramRuleItem(
                        label="Courses and module slots are different",
                        text=(
                            "A checklist box represents a degree module, not necessarily one particular "
                            "course. Different suitable courses may fit a broader module such as Aktuelle "
                            "Forschungsthemen, Spezielle Aspekte, or Ausgewählte Themen. Compare the "
                            "module description's learning outcomes, content, workload, and examination "
                            "requirements; a similar title or enough LP alone does not establish a fit."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Check for the course's own named module first",
                        text=(
                            "Check the canonical module slots below and the credited module shown in "
                            "the course listing before suggesting a broad slot. If the course has a "
                            "suitable dedicated module, prefer that approved placement when it fits the "
                            "rest of the plan. For example, a course confirmed as Telematik can use the "
                            "Telematik slot instead of consuming Ausgewählte Themen der Technischen "
                            "Informatik. Do not infer approval just from a matching name."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Keep flexible slots available for later semesters",
                        text=(
                            "Before filling a broad module slot, list courses you want to take now and "
                            "later and their possible target modules. Reserve a slot when a future "
                            "course may need it and use a suitable dedicated slot for today's course "
                            "where possible. Ask which slots are already used and which future courses "
                            "matter to you; make provisional suggestions if this is unknown. Future "
                            "course availability still needs confirmation from the offering university."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Courses at other universities",
                        text=(
                            "Courses from other universities can be candidates for a checklist module "
                            "when their learning outcomes and workload fit. Prepare a reasoned mapping "
                            "from the external course or combination of courses to the intended FU "
                            "module, supported by both module descriptions and the Leistungsnachweis. "
                            "Discuss recognition with the Prüfungsausschuss, preferably before committing "
                            "to the course. A convincing proposal supports the request; approval is not "
                            "automatic, and attendance/exam access must also be arranged with the host."
                        ),
                    ),
                    ProgramRuleItem(
                        label="One module slot is not an unlimited container",
                        text=(
                            "Many alternative courses may fit one module, but that does not allow you "
                            "to count that target module repeatedly or count the same course twice. "
                            "Respect the module's LP and assessment requirements, subject allocation, "
                            "specialization, and all seminar, project, grading, and prior-credit limits. "
                            "Distinct A/B modules are separate slots only where the catalogue lists them."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Read the slot list correctly",
                        text=(
                            "The following Informatik modules are checklist slots from the canonical "
                            "catalogue, not an exhaustive list of eligible courses or a timetable. "
                            "Anwendungsbereich and Wahlbereich follow their separate subject and "
                            "recognition rules. An arithmetic plan check does not decide whether an "
                            "external course fits a module or approve a recognition request."
                        ),
                    ),
                    *_checklist_slot_items(),
                ],
                sources=[*DEFAULT_SOURCES, EXAM_BOARD_SOURCE],
            ),
            ProgramRuleSection(
                id="wissenschaftliches-arbeiten",
                title="Wissenschaftliches Arbeiten",
                description=(
                    "Choose 2 to 4 Wissenschaftliches Arbeiten modules (seminars), 5 LP each. "
                    "The maximum of 4 applies to the whole plan, including Wahlbereich."
                ),
                items=[
                    ProgramRuleItem(
                        label="Core count",
                        text="At least 2 in the 70 LP Informatik area; at most 4 across the whole plan, including Wahlbereich.",
                        minimum=2,
                        maximum=4,
                        unit="modules",
                    ),
                    ProgramRuleItem(
                        label="Specialization coverage",
                        text="At least one Wissenschaftliches Arbeiten module in the Informatik allocation must come from your specialization subject.",
                        minimum=1,
                        unit="module",
                    ),
                    ProgramRuleItem(
                        label="No extra seminar allowance",
                        text="Allocating a seminar to Wahlbereich does not permit a fifth or sixth seminar.",
                    ),
                    ProgramRuleItem(
                        label="Duplicate modules",
                        text="The same exact Wissenschaftliches Arbeiten module can only be counted once.",
                    ),
                ],
                related_issue_codes=[
                    "scientific_work_count",
                    "scientific_work_specialization",
                    "duplicate_modules",
                    "wahlbereich_lp",
                ],
                sources=DEFAULT_SOURCES,
            ),
            ProgramRuleSection(
                id="softwareprojekt",
                title="Softwareprojekt",
                description=(
                    "Choose 1 or 2 Softwareprojekt modules, 10 LP each. "
                    "The maximum of 2 applies to the whole plan, including Wahlbereich."
                ),
                items=[
                    ProgramRuleItem(
                        label="Core count",
                        text="At least 1 in the 70 LP Informatik area; at most 2 across the whole plan, including Wahlbereich.",
                        minimum=1,
                        maximum=2,
                        unit="modules",
                    ),
                    ProgramRuleItem(
                        label="No extra project allowance",
                        text="Allocating a Softwareprojekt to Wahlbereich does not permit a third project.",
                    ),
                    ProgramRuleItem(
                        label="Grading",
                        text="Softwareprojekt A is graded; Softwareprojekt B is ungraded.",
                    ),
                ],
                related_issue_codes=["software_project_count", "wahlbereich_lp", "ungraded_lp"],
                sources=DEFAULT_SOURCES,
            ),
            ProgramRuleSection(
                id="ungraded-modules",
                title="Graded and Ungraded Modules",
                description=(
                    "Across the 90 LP taught modules, including Wahlbereich: 60 to 65 LP graded "
                    "and 25 to 30 LP ungraded. The Masterarbeit is separate."
                ),
                items=[
                    ProgramRuleItem(label="Graded LP", text="60 to 65 LP with differentiated grades, excluding the Masterarbeit.", minimum=60, maximum=65, unit="LP"),
                    ProgramRuleItem(
                        label="Ungraded LP",
                        text="Ungraded or non-differentiated modules must total 25 to 30 LP.",
                        minimum=25,
                        maximum=30,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Known examples",
                        text=(
                            "Known ungraded modules include Wissenschaftliches Arbeiten, Softwareprojekt B, "
                            "Projektmanagement, Projektmanagement - Vertiefung, Grundlagen des Managements "
                            "von IT-Projekten, Praktiken professioneller Softwareentwicklung, and "
                            "Existenzgruendung in der IT-Industrie."
                        ),
                    ),
                ],
                related_issue_codes=["ungraded_lp", "graded_lp"],
                sources=DEFAULT_SOURCES,
            ),
            ProgramRuleSection(
                id="bachelor-modules",
                title="Bachelor-Level Modules and Earlier Credits",
                description="Up to 15 LP of Bachelor-level modules may count, subject to eligibility and no double use of prior credits.",
                items=[
                    ProgramRuleItem(
                        label="Bachelor-module LP",
                        text="Bachelor modules can only be counted up to 15 LP.",
                        maximum=15,
                        unit="LP",
                    ),
                    ProgramRuleItem(
                        label="Additional credits only",
                        text="Credits earned while enrolled in a Bachelor may count only if they were additional to the credits used for that degree (normally 180 LP) and were not used to satisfy Master admission requirements. Recognition is decided by the Prüfungsausschuss.",
                    ),
                    ProgramRuleItem(
                        label="No double use",
                        text="A module already counted toward the Bachelor degree cannot count again, even if it is a Master-level module taken during the Bachelor. Merely exceeding 180 LP does not raise the 15 LP Bachelor-module cap (exam board decision, 26 October 2023).",
                    ),
                    ProgramRuleItem(
                        label="Unknown history",
                        text="The plan check needs your prior credit use to assess eligibility. If that information is missing, it reports a warning rather than assuming that Bachelor-level modules are transferable.",
                    ),
                    ProgramRuleItem(
                        label="Application modules",
                        text=(
                            "The 15 LP cap covers Bachelor-level modules in all three allocations, "
                            "including Anwendungsbereich and Wahlbereich. It does not automatically apply to "
                            "a Master-level module merely because it was taken during Bachelor enrollment."
                        ),
                    ),
                ],
                related_issue_codes=["bachelor_module_lp", "bachelor_credit_reuse", "admission_credit_reuse", "bachelor_credit_history_unknown"],
                sources=[*DEFAULT_SOURCES, EXAM_BOARD_SOURCE],
            ),
            ProgramRuleSection(
                id="duplicates",
                title="Duplicate and Incompatible Modules",
                description="Count each module once and check earlier Bachelor credit use as well as excluded module combinations.",
                items=[
                    ProgramRuleItem(
                        label="Exact duplicate",
                        text="The same exact module cannot count twice in the Master.",
                    ),
                    ProgramRuleItem(
                        label="Incompatible project-management modules",
                        text="Projektmanagement cannot be combined with Grundlagen des Managements von IT-Projekten or Projektmanagement - Vertiefung (§7(9)); moving one into Wahlbereich does not remove this restriction.",
                    ),
                    ProgramRuleItem(
                        label="Previously used Master modules",
                        text=(
                            "A Master module already used in a prior Bachelor specialization cannot be reused "
                            "for the Master."
                        ),
                    ),
                ],
                related_issue_codes=["duplicate_modules", "bachelor_credit_reuse", "admission_credit_reuse", "project_management_conflict"],
                sources=DEFAULT_SOURCES,
            ),
            ProgramRuleSection(
                id="cross-university-courses",
                title="Courses at HU Berlin and TU Berlin (Nebenhörerschaft)",
                description=(
                    "Modules taken as a cross-registered student ('Nebenhörer', also called "
                    "Zweithörerschaft) at Humboldt-Universität or Technische Universität Berlin can be "
                    "recognized for the Master Informatik, either as general area credit or, when "
                    "content matches, as a specific FU module. The steps below describe the practical "
                    "process."
                ),
                items=[
                    ProgramRuleItem(
                        label="Legal basis",
                        text=(
                            "Berlin's universities (FU, HU, TU, UdK) allow students to attend and be "
                            "examined in individual courses at a partner university as a Nebenhörer, "
                            "in addition to normal enrollment at their home university."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Step 1 - Find a course",
                        text=(
                            "Browse the host university's Vorlesungsverzeichnis for a module that "
                            "interests you and fits your Stundenplan: the "
                            "[TU Berlin Moses Vorlesungsverzeichnis](https://moseskonto.tu-berlin.de/moses/verzeichnis/veranstaltungen/vkpl_stg.html) "
                            "or the [HU Berlin Agnes Vorlesungsverzeichnis](https://agnes.hu-berlin.de/lupo/rds?state=change&type=5&"
                            "moduleParameter=abstgvSearch&nextdir=change&next=search.vm&subdir=stg&clean=y&"
                            "category=curricula.search&navigationPosition=lectures%2Ccurriculaschedules&"
                            "breadcrumb=curriculaschedules&topitem=lectures&subitem=curriculaschedules) "
                            "(if the deep link is broken, start at [agnes.hu-berlin.de](https://agnes.hu-berlin.de/))."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Step 2 - Optional pre-check with the Prüfungsausschuss",
                        text=(
                            "Ask the Prüfungsausschuss chair by email or in person whether the "
                            "course could be credited. Contact details are on the "
                            "[exam board page](https://www.mi.fu-berlin.de/fb/beauf-aussch/pruefungsausschuss-inf-master/index.html). "
                            "The chair may not have time or may decline to assess a course you have not "
                            "taken yet; trying first and then deciding is still recommended."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Step 3 - Ask the teacher",
                        text=(
                            "Email the teacher of the HU/TU module and ask whether you may participate "
                            "as Nebenhörer. Attach the filled Nebenhörer application form: the "
                            "[HU form (PDF)](https://www.hu-berlin.de/fileadmin/Mediathek/Zentrale_Seiten/Studium/Dokumente/Studium_Anmeldung_Gasthorerschaft_Nebenhoererschaft_20210323.pdf) "
                            "or the [TU form (PDF)](https://www.static.tu.berlin/fileadmin/www/10002460/Bewerben_und_Einschreiben/GH_NH/Nebenhoererschein_SLM.pdf)."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Step 4 - Submit the Nebenhörer application",
                        text=(
                            "If the teacher agrees and signs, send the document to the responsible "
                            "office to validate the Nebenhörerantrag; the office is named on the form "
                            "and on the general information pages (see the "
                            "[HU Nebenhörerschaft page](https://www.hu-berlin.de/studium/nach-dem-studium/lebenslanges-lernen/gasthoerer-und-nebenhoererschaft) "
                            "and the [TU Nebenhörerschaft page](https://www.tu.berlin/studierendensekretariat/themen-a-z/gast-und-nebenhoererschaft/)). "
                            "These pages cover only the Nebenhörer enrollment at the host "
                            "university, not the later recognition at FU (that is Step 5). "
                            "The office can take time to answer - follow up by email if needed, and "
                            "attend the course from the start even while the confirmation is pending."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Taking the exam",
                        text=(
                            "Attend the course and sit the exam at the host university like one of its "
                            "own students; the host university issues a Leistungsnachweis with grade and "
                            "workload (LP or ECTS)."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Step 5 - Recognition at FU",
                        text=(
                            "At the end of the semester, register the recognition request online on the "
                            "[MVS platform](https://kvv.imp.fu-berlin.de/mvs2/) - the procedure is "
                            "explained under 'Anrechnung von Leistungen' (Anerkennung, RSPO §7, "
                            "M SPO §9(14)) on the "
                            "[Prüfungsausschuss Informatik page](https://www.mi.fu-berlin.de/w/Inf/PruefungsAusschuss) - "
                            "and then book an in-person appointment with the "
                            "Prüfungsausschuss chair to explain why you took the course and how "
                            "it should count. Bring the Leistungsnachweis and the HU/TU module "
                            "description (Modulbeschreibung)."
                        ),
                    ),
                    ProgramRuleItem(
                        label="General-area recognition",
                        text=(
                            "Courses in a suitable scientific subject may be proposed for recognition in the "
                            "Anwendungsbereich (which is explicitly meant to draw on subjects outside "
                            "Informatik) or in the Wahlbereich, without needing to match an existing "
                            "Informatik module title. Both routes require the appropriate recognition "
                            "decision; a thematic match alone is not approval."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Module-equivalence recognition",
                        text=(
                            "If a HU/TU course's content and workload substantially match a specific "
                            "Informatik module ('passt in eine Modulhülle'), the Prüfungsausschuss can "
                            "instead recognize it as that module, so it counts toward the practical, "
                            "technical, or theoretical specialization areas rather than only "
                            "Anwendungsbereich or Wahlbereich."
                        ),
                    ),
                    ProgramRuleItem(
                        label="No double counting",
                        text=(
                            "Recognized external credit follows the same no-double-counting rule as FU "
                            "modules: the same content can only be counted once in the plan."
                        ),
                    ),
                    ProgramRuleItem(
                        label="Links and contacts change",
                        text=(
                            "Chairs rotate and URLs move; if a link no longer works, start from the "
                            "HU/TU Nebenhörerschaft pages or the FU Informatik Prüfungsausschuss page. "
                            "The final recognition decision always lies with the Prüfungsausschuss."
                        ),
                    ),
                ],
                sources=CROSS_UNIVERSITY_SOURCES,
            ),
        ],
    )
