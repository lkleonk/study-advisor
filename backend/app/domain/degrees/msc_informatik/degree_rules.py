from collections import Counter
from typing import Any, Literal

from app.domain.module_catalog import enrich_study_plan, normalize_module_name
from app.domain.rule_check import RuleCheckResult, RuleIssue
from app.domain.study_plan import StudyPlan


INFORMATICS_AREAS = {"practical", "theoretical", "technical"}
SPECIALIZATION_MINIMUMS = {
    "practical": {"normal": 20, "specialization": 40},
    "technical": {"normal": 10, "specialization": 30},
    "theoretical": {"normal": 10, "specialization": 30},
}


def _sum_lp(plan: StudyPlan, predicate) -> int:
    return sum(module.lp for module in plan.modules if predicate(module))


def validate_study_plan(raw_plan: StudyPlan | dict[str, Any]) -> RuleCheckResult:
    plan = StudyPlan.model_validate(raw_plan)
    plan = enrich_study_plan(plan)
    issues: list[RuleIssue] = []

    def add_issue(code: str, severity: Literal["error", "warning"], message: str, **details: Any) -> None:
        issues.append(RuleIssue(code=code, severity=severity, message=message, details=details))

    for module in plan.modules:
        if module.lp <= 0:
            add_issue(
                "module_lp_missing",
                "error",
                f"Module '{module.name}' has no LP value.",
                module=module.name,
            )

    module_area_lp = _sum_lp(plan, lambda module: module.area != "thesis")
    thesis_lp = _sum_lp(plan, lambda module: module.area == "thesis")
    informatics_lp = _sum_lp(plan, lambda module: module.area in INFORMATICS_AREAS and not module.is_wahlbereich)
    application_lp = _sum_lp(plan, lambda module: module.area == "application" and not module.is_wahlbereich)
    ungraded_lp = _sum_lp(plan, lambda module: module.area != "thesis" and module.is_ungraded)
    graded_lp = module_area_lp - ungraded_lp
    bachelor_lp = _sum_lp(plan, lambda module: module.area != "thesis" and module.is_bachelor_module)
    wahlbereich_lp = _sum_lp(plan, lambda module: module.area != "thesis" and module.is_wahlbereich)
    core_scientific_work_count = sum(
        1 for module in plan.modules
        if module.is_scientific_work and module.area in INFORMATICS_AREAS and not module.is_wahlbereich
    )
    total_scientific_work_count = sum(1 for module in plan.modules if module.is_scientific_work)
    core_software_project_count = sum(
        1 for module in plan.modules
        if module.is_software_project and module.area in INFORMATICS_AREAS and not module.is_wahlbereich
    )
    total_software_project_count = sum(1 for module in plan.modules if module.is_software_project)

    area_totals = {
        "practical_lp": _sum_lp(plan, lambda module: module.area == "practical" and not module.is_wahlbereich),
        "theoretical_lp": _sum_lp(plan, lambda module: module.area == "theoretical" and not module.is_wahlbereich),
        "technical_lp": _sum_lp(plan, lambda module: module.area == "technical" and not module.is_wahlbereich),
        "application_lp": application_lp,
        "informatics_lp": informatics_lp,
        "module_area_lp": module_area_lp,
        "thesis_lp": thesis_lp,
        "master_total_lp": module_area_lp + thesis_lp if thesis_lp else module_area_lp + 30,
        "ungraded_lp": ungraded_lp,
        "graded_lp": graded_lp,
        "bachelor_module_lp": bachelor_lp,
        "wahlbereich_lp": wahlbereich_lp,
        "core_scientific_work_count": core_scientific_work_count,
        "total_scientific_work_count": total_scientific_work_count,
        "core_software_project_count": core_software_project_count,
        "total_software_project_count": total_software_project_count,
    }

    if module_area_lp != 90:
        add_issue(
            "module_area_lp_total",
            "error",
            "The taught modules must total exactly 90 LP: 70 Informatik, 10 Anwendungsbereich, and 10 Wahlbereich.",
            current_lp=module_area_lp,
            required_lp=90,
            delta=module_area_lp - 90,
        )

    if thesis_lp not in {0, 30}:
        add_issue(
            "master_thesis_lp",
            "error",
            "The Masterarbeit must count as 30 LP when it is included in the plan.",
            current_lp=thesis_lp,
            required_lp=30,
        )

    if informatics_lp != 70:
        add_issue(
            "informatics_area_lp",
            "error",
            "The Informatik area must contain exactly 70 LP, excluding Wahlbereich modules.",
            current_lp=informatics_lp,
            required_lp=70,
        )

    if application_lp != 10:
        add_issue(
            "application_area_lp",
            "error",
            "The Anwendungsbereich must contain exactly 10 LP, excluding Wahlbereich modules.",
            current_lp=application_lp,
            required_lp=10,
        )

    specialization = plan.specialization_area
    if specialization is None:
        add_issue(
            "specialization_missing",
            "error",
            "Exactly one specialization area must be selected: practical, theoretical, or technical.",
        )

    for area, limits in SPECIALIZATION_MINIMUMS.items():
        required_lp = limits["specialization"] if specialization == area else limits["normal"]
        current_lp = area_totals[f"{area}_lp"]
        if current_lp < required_lp:
            add_issue(
                f"{area}_minimum_lp",
                "error",
                f"{area.capitalize()} Informatics requires at least {required_lp} LP.",
                current_lp=current_lp,
                required_lp=required_lp,
                specialization_area=specialization,
            )

    if wahlbereich_lp != 10:
        add_issue(
            "wahlbereich_lp",
            "error",
            "The separate Wahlbereich must contain exactly 10 LP from Informatik or other scientific subjects.",
            current_lp=wahlbereich_lp,
            required_lp=10,
        )

    if any(module.area == "thesis" and module.is_wahlbereich for module in plan.modules):
        add_issue("wahlbereich_thesis", "error", "The Masterarbeit cannot be allocated to Wahlbereich.")

    if core_scientific_work_count < 2 or total_scientific_work_count > 4:
        add_issue(
            "scientific_work_count",
            "error",
            "Choose 2 to 4 Wissenschaftliches Arbeiten modules, with at least 2 in Informatik; the maximum includes Wahlbereich.",
            current_count=total_scientific_work_count,
            core_count=core_scientific_work_count,
            minimum_count=2,
            maximum_count=4,
            total_count=total_scientific_work_count,
        )

    if specialization is not None:
        has_scientific_work_in_specialization = any(
            module.is_scientific_work and module.area == specialization and not module.is_wahlbereich
            for module in plan.modules
        )
        if not has_scientific_work_in_specialization:
            add_issue(
                "scientific_work_specialization",
                "error",
                "At least one Wissenschaftliches Arbeiten module must be from the specialization area.",
                specialization_area=specialization,
            )

    if core_software_project_count < 1 or total_software_project_count > 2:
        add_issue(
            "software_project_count",
            "error",
            "Choose 1 or 2 Softwareprojekt modules, with at least 1 in Informatik; the maximum includes Wahlbereich.",
            current_count=total_software_project_count,
            core_count=core_software_project_count,
            minimum_count=1,
            maximum_count=2,
            total_count=total_software_project_count,
        )

    if not 25 <= ungraded_lp <= 30:
        add_issue(
            "ungraded_lp",
            "error",
            "Ungraded or non-differentiated modules must total 25 to 30 LP.",
            current_lp=ungraded_lp,
            minimum_lp=25,
            maximum_lp=30,
        )

    if bachelor_lp > 15:
        add_issue(
            "bachelor_module_lp",
            "error",
            "Bachelor modules can only be counted up to 15 LP.",
            current_lp=bachelor_lp,
            maximum_lp=15,
        )

    if not 60 <= graded_lp <= 65:
        add_issue(
            "graded_lp", "error", "Graded taught modules must total 60 to 65 LP, excluding the Masterarbeit.",
            current_lp=graded_lp, minimum_lp=60, maximum_lp=65,
        )

    reused_modules = [module.name for module in plan.modules if module.counted_in_bachelor is True]
    if reused_modules:
        add_issue(
            "bachelor_credit_reuse", "error",
            "Modules already counted toward the Bachelor degree cannot count again in the Master, including Master-level modules.",
            modules=reused_modules,
        )
    admission_modules = [module.name for module in plan.modules if module.used_for_master_admission is True]
    if admission_modules:
        add_issue(
            "admission_credit_reuse", "error",
            "Modules used to satisfy Master admission requirements cannot also count toward the Master degree.",
            modules=admission_modules,
        )
    unknown_bachelor_history = [
        module.name for module in plan.modules
        if module.is_bachelor_module
        and module.counted_in_bachelor is not True
        and module.used_for_master_admission is not True
        and (module.counted_in_bachelor is None or module.used_for_master_admission is None)
    ]
    if unknown_bachelor_history:
        add_issue(
            "bachelor_credit_history_unknown", "warning",
            "Confirm that these Bachelor-level modules are outside the Bachelor degree credits (normally 180 LP) and were not used for Master admission; the 15 LP cap alone does not establish eligibility.",
            modules=unknown_bachelor_history,
        )

    names = {normalize_module_name(module.name) for module in plan.modules}
    incompatible = names & {
        normalize_module_name("Grundlagen des Managements von IT-Projekten"),
        normalize_module_name("Projektmanagement - Vertiefung"),
    }
    if normalize_module_name("Projektmanagement") in names and incompatible:
        add_issue(
            "project_management_conflict", "error",
            "Projektmanagement cannot be combined with Grundlagen des Managements von IT-Projekten or Projektmanagement - Vertiefung (SPO §7(9)).",
            conflicting_modules=sorted(incompatible),
        )

    normalized_names = [normalize_module_name(module.name) for module in plan.modules if module.name.strip()]
    duplicate_names = sorted(name for name, count in Counter(normalized_names).items() if count > 1)
    if duplicate_names:
        add_issue(
            "duplicate_modules",
            "error",
            "The same exact module cannot count twice.",
            duplicate_normalized_names=duplicate_names,
        )

    unknown_area_modules = [
        module.name for module in plan.modules if module.area == "unknown" and module.area != "thesis"
    ]
    if unknown_area_modules:
        add_issue(
            "unknown_module_area",
            "warning",
            "Some modules could not be assigned to an area; verify their official area manually.",
            modules=unknown_area_modules,
        )

    is_valid = not any(issue.severity == "error" for issue in issues)
    if is_valid:
        summary = "The supplied study plan satisfies the implemented 2014 Master Informatik checks."
        if any(issue.severity == "warning" for issue in issues):
            summary += " Warnings require confirmation before credit eligibility can be established."
    else:
        error_count = sum(1 for issue in issues if issue.severity == "error")
        summary = f"The supplied study plan has {error_count} blocking issue(s) under the implemented checks."

    return RuleCheckResult(
        is_valid=is_valid,
        summary=summary,
        totals=area_totals,
        issues=issues,
    )
