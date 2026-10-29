import pytest

from app.domain.degrees.msc_informatik.degree_rules import validate_study_plan


def issue_codes(result):
    return {issue.code for issue in result.issues}


def valid_plan():
    return {
        "specialization_area": "practical",
        "modules": [
            {"name": "Softwareprojekt Praktische Informatik B"},
            {"name": "Wissenschaftliches Arbeiten Praktische Informatik A"},
            {"name": "Projektmanagement"},
            {"name": "Künstliche Intelligenz"},
            {"name": "Datenbanktechnologie"},
            {"name": "Rechnersicherheit"},
            {"name": "Algorithmische Geometrie"},
            {"name": "Modelchecking", "is_wahlbereich": True},
            {"name": "Betriebssysteme"},
            {"name": "Wissenschaftliches Arbeiten Technische Informatik A"},
            {"name": "Mobilkommunikation"},
            {"name": "Anwendungsmodul A", "lp": 10, "area": "application"},
            {"name": "Masterarbeit"},
        ],
    }


def test_valid_plan_passes():
    result = validate_study_plan(valid_plan())

    assert result.is_valid
    assert result.totals["module_area_lp"] == 90
    assert result.totals["informatics_lp"] == 70
    assert result.totals["application_lp"] == 10
    assert result.totals["wahlbereich_lp"] == 10
    assert result.totals["graded_lp"] == 65
    assert result.totals["ungraded_lp"] == 25
    assert result.totals["core_software_project_count"] == 1
    assert result.totals["core_scientific_work_count"] == 2


def test_missing_specialization_lp_fails():
    plan = valid_plan()
    plan["specialization_area"] = "technical"

    result = validate_study_plan(plan)

    assert not result.is_valid
    assert "technical_minimum_lp" in issue_codes(result)


def test_too_many_ungraded_lp_fails():
    plan = valid_plan()
    plan["modules"][-2]["is_ungraded"] = True

    result = validate_study_plan(plan)

    assert not result.is_valid
    assert "ungraded_lp" in issue_codes(result)


def test_too_many_bachelor_module_lp_fails():
    plan = valid_plan()
    plan["modules"][-2]["lp"] = 20
    plan["modules"][-2]["is_bachelor_module"] = True

    result = validate_study_plan(plan)

    assert not result.is_valid
    assert "bachelor_module_lp" in issue_codes(result)


def test_too_few_scientific_work_modules_fails():
    plan = valid_plan()
    plan["modules"] = [
        module
        for module in plan["modules"]
        if module["name"] != "Wissenschaftliches Arbeiten Technische Informatik A"
    ]
    plan["modules"].append({"name": "Telematik"})

    result = validate_study_plan(plan)

    assert not result.is_valid
    assert "scientific_work_count" in issue_codes(result)


def test_too_many_software_projects_fails():
    plan = valid_plan()
    plan["modules"].append({"name": "Softwareprojekt - Technische Informatik A"})
    plan["modules"].append({"name": "Softwareprojekt - Theoretische Informatik A"})

    result = validate_study_plan(plan)

    assert not result.is_valid
    assert "software_project_count" in issue_codes(result)


def test_third_software_project_rejected_even_when_in_wahlbereich():
    plan = valid_plan()
    plan["modules"] = [
        {"name": "Softwareprojekt Praktische Informatik B"},
        {"name": "Softwareprojekt - Theoretische Informatik A"},
        {
            "name": "Softwareprojekt - Technische Informatik A",
            "is_wahlbereich": True,
        },
        {"name": "Wissenschaftliches Arbeiten Praktische Informatik A"},
        {"name": "Projektmanagement"},
        {"name": "Künstliche Intelligenz"},
        {"name": "Datenbanktechnologie"},
        {"name": "Rechnersicherheit"},
        {"name": "Algorithmische Geometrie"},
        {"name": "Wissenschaftliches Arbeiten Technische Informatik A"},
        {"name": "Mobilkommunikation"},
        {"name": "Anwendungsmodul A", "lp": 10, "area": "application"},
        {"name": "Masterarbeit"},
    ]

    result = validate_study_plan(plan)

    assert not result.is_valid
    assert "software_project_count" in issue_codes(result)
    assert result.totals["core_software_project_count"] == 2
    assert result.totals["total_software_project_count"] == 3
    assert result.totals["wahlbereich_lp"] == 10


def test_six_scientific_work_modules_rejected_even_when_two_in_wahlbereich():
    plan = {
        "specialization_area": "practical",
        "modules": [
            {"name": "Softwareprojekt Praktische Informatik A"},
            {"name": "Wissenschaftliches Arbeiten Praktische Informatik A"},
            {"name": "Wissenschaftliches Arbeiten Praktische Informatik B"},
            {"name": "Wissenschaftliches Arbeiten Technische Informatik A"},
            {"name": "Wissenschaftliches Arbeiten Technische Informatik B"},
            {
                "name": "Wissenschaftliches Arbeiten Theoretische Informatik A",
                "is_wahlbereich": True,
            },
            {
                "name": "Wissenschaftliches Arbeiten Theoretische Informatik B",
                "is_wahlbereich": True,
            },
            {"name": "Künstliche Intelligenz"},
            {"name": "Datenbanktechnologie"},
            {"name": "Rechnersicherheit"},
            {"name": "Telematik"},
            {"name": "Algorithmische Geometrie"},
            {"name": "Anwendungsmodul A", "lp": 10, "area": "application"},
            {"name": "Masterarbeit"},
        ],
    }

    result = validate_study_plan(plan)

    assert not result.is_valid
    assert "scientific_work_count" in issue_codes(result)
    assert result.totals["core_scientific_work_count"] == 4
    assert result.totals["total_scientific_work_count"] == 6
    assert result.totals["wahlbereich_lp"] == 10


@pytest.mark.parametrize("specialization", ["practical", "technical", "theoretical"])
@pytest.mark.parametrize("free_area", ["practical", "technical", "theoretical"])
@pytest.mark.parametrize("elective_area", ["practical", "technical", "theoretical", "application"])
def test_separate_allocations_allow_each_specialization_and_free_choice(specialization, free_area, elective_area):
    totals = {"practical": 20, "technical": 10, "theoretical": 10}
    totals[specialization] += 20
    totals[free_area] += 10
    other_seminar_area = "theoretical" if specialization != "theoretical" else "technical"
    modules = [
        {"name": "Project", "lp": 10, "area": "practical", "is_software_project": True, "is_ungraded": True},
        {"name": "Specialization seminar", "lp": 5, "area": specialization, "is_scientific_work": True, "is_ungraded": True},
        {"name": "Other seminar", "lp": 5, "area": other_seminar_area, "is_scientific_work": True, "is_ungraded": True},
        {"name": "Skills", "lp": 5, "area": "practical", "is_ungraded": True},
    ]
    for area, lp in totals.items():
        used = sum(m["lp"] for m in modules if m["area"] == area)
        if lp > used:
            modules.append({"name": f"Lectures in {area}", "lp": lp - used, "area": area})
    modules.extend([
        {"name": "Application subject", "lp": 10, "area": "application"},
        {"name": "Elective subject", "lp": 10, "area": elective_area, "is_wahlbereich": True},
        {"name": "Masterarbeit"},
    ])
    result = validate_study_plan({"specialization_area": specialization, "modules": modules})
    assert result.is_valid, result.issues
    assert not result.issues
    assert result.totals["informatics_lp"] == 70
    assert result.totals["application_lp"] == result.totals["wahlbereich_lp"] == 10
    assert {area: result.totals[f"{area}_lp"] for area in totals} == totals


def test_wahlbereich_cannot_supply_specialization_credits():
    plan = valid_plan()
    for module in plan["modules"]:
        if module["name"] == "Modelchecking":
            module["is_wahlbereich"] = False
        if module["name"] == "Rechnersicherheit":
            module["is_wahlbereich"] = True
    result = validate_study_plan(plan)
    assert result.totals["informatics_lp"] == 70
    assert result.totals["practical_lp"] == 30
    assert "practical_minimum_lp" in issue_codes(result)


@pytest.mark.parametrize("legacy_area", ["theoretical", "application"])
def test_missing_wahlbereich_is_not_silently_folded_into_other_areas(legacy_area):
    plan = valid_plan()
    elective = next(m for m in plan["modules"] if m["name"] == "Modelchecking")
    elective.update(is_wahlbereich=False, area=legacy_area)
    result = validate_study_plan(plan)
    assert "wahlbereich_lp" in issue_codes(result)
    assert ("informatics_area_lp" if legacy_area == "theoretical" else "application_area_lp") in issue_codes(result)


def test_second_project_in_wahlbereich_is_within_whole_plan_cap():
    plan = valid_plan()
    elective = next(m for m in plan["modules"] if m["name"] == "Modelchecking")
    elective["name"] = "Softwareprojekt - Technische Informatik A"
    result = validate_study_plan(plan)
    assert result.is_valid, result.issues
    assert result.totals["total_software_project_count"] == 2


@pytest.mark.parametrize("module_name,code", [
    ("Softwareprojekt Praktische Informatik B", "software_project_count"),
    ("Wissenschaftliches Arbeiten Technische Informatik A", "scientific_work_count"),
])
def test_wahlbereich_does_not_supply_required_informatik_project_or_seminars(module_name, code):
    plan = valid_plan()
    next(m for m in plan["modules"] if m["name"] == module_name)["is_wahlbereich"] = True
    assert code in issue_codes(validate_study_plan(plan))


def test_four_seminars_with_two_in_wahlbereich_stay_within_cap():
    plan = valid_plan()
    plan["modules"][0]["name"] = "Softwareprojekt Praktische Informatik A"
    plan["modules"] = [m for m in plan["modules"] if m["name"] != "Modelchecking"]
    for suffix in ("A", "B"):
        plan["modules"].append({"name": f"Wissenschaftliches Arbeiten Theoretische Informatik {suffix}", "is_wahlbereich": True})
    result = validate_study_plan(plan)
    assert result.is_valid, result.issues
    assert result.totals["total_scientific_work_count"] == 4


@pytest.mark.parametrize("in_wahlbereich", [False, True])
def test_fifth_seminar_is_always_rejected(in_wahlbereich):
    plan = valid_plan()
    for index in range(3):
        plan["modules"].append({"name": f"Extra seminar {index}", "lp": 5, "area": "theoretical", "is_scientific_work": True, "is_wahlbereich": in_wahlbereich})
    assert "scientific_work_count" in issue_codes(validate_study_plan(plan))


def test_bachelor_level_cap_includes_application_and_wahlbereich():
    plan = valid_plan()
    for module in plan["modules"]:
        if module["name"] in {"Anwendungsmodul A", "Modelchecking"}:
            module.update(is_bachelor_module=True, counted_in_bachelor=False, used_for_master_admission=False)
    result = validate_study_plan(plan)
    assert result.totals["bachelor_module_lp"] == 20
    assert "bachelor_module_lp" in issue_codes(result)


@pytest.mark.parametrize("flag,code", [("counted_in_bachelor", "bachelor_credit_reuse"), ("used_for_master_admission", "admission_credit_reuse")])
@pytest.mark.parametrize("bachelor_level", [False, True])
def test_reused_credits_are_rejected_regardless_of_module_level(flag, code, bachelor_level):
    plan = valid_plan()
    plan["modules"][3].update(is_bachelor_module=bachelor_level, **{flag: True})
    result = validate_study_plan(plan)
    assert not result.is_valid
    assert code in issue_codes(result)


def test_fifteen_extra_bachelor_level_lp_can_pass_with_confirmed_credit_history():
    plan = valid_plan()
    for module in plan["modules"]:
        if module["name"] in {"Anwendungsmodul A", "Künstliche Intelligenz"}:
            module.update(is_bachelor_module=True, counted_in_bachelor=False, used_for_master_admission=False)
    result = validate_study_plan(plan)
    assert result.is_valid and not result.issues
    assert result.totals["bachelor_module_lp"] == 15


@pytest.mark.parametrize("known_flags", [{}, {"counted_in_bachelor": False}, {"used_for_master_admission": False}])
def test_unknown_bachelor_credit_history_requires_confirmation(known_flags):
    plan = valid_plan()
    plan["modules"][-2].update(is_bachelor_module=True, **known_flags)
    result = validate_study_plan(plan)
    warning = next(i for i in result.issues if i.code == "bachelor_credit_history_unknown")
    assert warning.severity == "warning"
    assert "confirmation" in result.summary


@pytest.mark.parametrize("other_module", ["Projektmanagement - Vertiefung", "Grundlagen des Managements von IT-Projekten"])
def test_incompatible_project_management_modules_are_rejected(other_module):
    plan = valid_plan()
    plan["modules"].append({"name": other_module, "is_wahlbereich": True})
    assert "project_management_conflict" in issue_codes(validate_study_plan(plan))


def test_duplicate_master_module_is_rejected():
    plan = valid_plan()
    plan["modules"].append({"name": "Rechnersicherheit", "is_wahlbereich": True})
    assert "duplicate_modules" in issue_codes(validate_study_plan(plan))


def test_thesis_cannot_fill_wahlbereich_and_does_not_change_taught_grading_totals():
    plan = valid_plan()
    plan["modules"][-1].update(is_wahlbereich=True, is_ungraded=True)
    result = validate_study_plan(plan)
    assert "wahlbereich_thesis" in issue_codes(result)
    assert result.totals["wahlbereich_lp"] == 10
    assert result.totals["ungraded_lp"] == 25
    assert result.totals["graded_lp"] == 65
