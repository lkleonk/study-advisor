import pytest

from fastapi.testclient import TestClient

from app.domain.degrees.msc_informatik.program_rules import get_program_rules
from app.domain.degrees import get_degree
from app.domain.program_rules import CROSS_UNIVERSITY_RULE_SECTION_ID, render_rules_context
from app.main import app


def section_by_id(section_id: str):
    catalogue = get_program_rules()
    return next(section for section in catalogue.sections if section.id == section_id)


def test_program_rules_apply_softwareprojekt_limit_to_whole_plan():
    section = section_by_id("softwareprojekt")
    text = " ".join(item.text for item in section.items)

    assert "Wahlbereich" in text
    assert "at most 2 across the whole plan" in text
    assert "does not permit a third project" in text
    assert "software_project_count" in section.related_issue_codes


def test_program_rules_apply_seminar_limit_to_whole_plan():
    section = section_by_id("wissenschaftliches-arbeiten")
    text = " ".join(item.text for item in section.items)

    assert "at most 4 across the whole plan" in text
    assert "does not permit a fifth or sixth seminar" in text
    assert "scientific_work_count" in section.related_issue_codes


def test_program_rules_endpoint_returns_catalogue():
    response = TestClient(app).get("/api/program-rules")

    assert response.status_code == 200
    body = response.json()
    assert body["degree_program"] == "FU Berlin Master Informatik"
    assert {section["id"] for section in body["sections"]} >= {
        "overall-structure",
        "informatics-area",
        "softwareprojekt",
        "wissenschaftliches-arbeiten",
        "module-rebooking",
        "professional-experience",
        "exam-registration",
        "exam-attempts-and-improvement",
        "study-abroad",
    }


def test_rules_context_is_rendered_from_program_rules():
    rules_context = render_rules_context(get_program_rules())

    assert "FU Berlin Master Informatik" in rules_context
    assert "COURSES AT HU BERLIN AND TU BERLIN" in rules_context


def test_rules_context_matches_corrected_structure_and_project_limits():
    rules_context = render_rules_context(get_program_rules())

    assert "70 LP Informatik + 10 LP Anwendungsbereich + 10 LP Wahlbereich + 30 LP Masterarbeit" in rules_context
    assert "at most 2 across the whole plan, including Wahlbereich" in rules_context
    assert "allowing 3 Softwareprojekt modules total" not in rules_context


def test_rules_context_can_exclude_cross_university_section():
    rules_context = render_rules_context(
        get_program_rules(),
        exclude_section_ids={CROSS_UNIVERSITY_RULE_SECTION_ID},
    )

    assert "COURSES AT HU BERLIN AND TU BERLIN" not in rules_context
    assert "SOFTWAREPROJEKT" in rules_context


CLASSIFIER_SYSTEM_PROMPT = get_degree("msc_informatik").prompts.classifier_system_prompt


def test_classifier_prompt_does_not_include_degree_rule_catalogue():
    assert "COURSES AT HU BERLIN AND TU BERLIN" not in CLASSIFIER_SYSTEM_PROMPT
    assert "At least 1 and at most 2 core Softwareprojekt" not in CLASSIFIER_SYSTEM_PROMPT
    assert "include_cross_university_rules" in CLASSIFIER_SYSTEM_PROMPT


def test_degree_parts_are_separate_and_shown_before_cross_cutting_rules():
    sections = get_program_rules().sections
    assert [s.id for s in sections[:5]] == [
        "overall-structure", "informatics-area", "application-area", "wahlbereich", "masterarbeit",
    ]
    for section_id, expected in [("informatics-area", 70), ("application-area", 10), ("wahlbereich", 10)]:
        volume = section_by_id(section_id).items[0]
        assert volume.minimum == volume.maximum == expected
    informatics = section_by_id("informatics-area")
    assert {item.label for item in informatics.items} >= {
        "Step 1 - Praktische Informatik", "Step 1 - Technische Informatik", "Step 1 - Theoretische Informatik",
        "Step 2 - Specialization (Vertiefung)", "Step 3 - Free Informatik choice",
    }


def test_catalogue_explains_prior_credit_reuse_and_advisory_scope():
    context = render_rules_context(get_program_rules())
    assert "normally 180 LP" in context
    assert "Master admission requirements" in context
    assert "26 October 2023" in context
    assert "project-management modules" in context
    assert "advisory" in get_program_rules().source_note
    assert "for a binding plan check" not in context


def test_master_thesis_can_start_after_sixty_lp_not_ninety():
    section = section_by_id("masterarbeit")
    assert section.items[0].minimum == 60
    assert "not a prerequisite" in section.items[0].text


def test_checklist_module_slots_match_the_canonical_catalogue():
    from app.domain.module_catalog import load_catalog

    section = section_by_id("checklist-planning")
    reference = "\n".join(item.text for item in section.items)
    for module in load_catalog().values():
        if module.area in {"practical", "technical", "theoretical"}:
            assert f"- {module.name} ({module.lp} LP)" in reference
    assert any(source.path == "https://www.mi.fu-berlin.de/w/Inf/PruefungsAusschuss" for source in section.sources)
    assert "module_catalog_name" not in reference  # User-facing wording, not schema keys.


def test_checklist_planning_survives_cross_university_context_filter():
    context = render_rules_context(
        get_program_rules(), exclude_section_ids={CROSS_UNIVERSITY_RULE_SECTION_ID},
    )
    assert "CHECKLIST AND KEEP OPTIONS OPEN" in context
    assert "Telematik (10 LP)" in context
    assert "Ausgewählte Themen der Technischen Informatik (10 LP)" in context
    assert "future course may need it" in context
    assert "approval is not automatic" in context
    assert "count that target module repeatedly" in context
    assert "COURSES AT HU BERLIN AND TU BERLIN" not in context


@pytest.mark.parametrize("section_id", [
    "module-rebooking", "professional-experience", "exam-registration",
    "exam-attempts-and-improvement", "study-abroad",
])
def test_administrative_guidance_is_available_without_cross_university_context(section_id):
    section = section_by_id(section_id)
    context = render_rules_context(
        get_program_rules(), exclude_section_ids={CROSS_UNIVERSITY_RULE_SECTION_ID},
    )
    assert section.title.upper() in context
    assert not section.related_issue_codes  # No automatic verdict without the relevant records.
    assert section.sources and all(s.path.startswith("https://") for s in section.sources)


def test_completed_module_rebooking_keeps_its_grade_restrictions():
    text = " ".join(item.text for item in section_by_id("module-rebooking").items)
    assert "only when A is ungraded" in text
    assert "A completed graded A cannot be moved" in text
    assert "grade 4.0" in text
    assert "does not authorize a rebooking" in text


def test_work_recognition_is_one_project_outside_enrollment_and_requires_assessment():
    section = section_by_id("professional-experience")
    text = " ".join(item.text for item in section.items)
    assert section.items[0].maximum == 10
    assert "replace one Softwareprojekt" in text
    assert "31 October 2025" in text
    assert "outside university enrollment" in text
    assert "employer letter" in text and "employment reference" in text
    assert "not add 10 LP on top" in text


def test_registration_distinguishes_general_deadline_and_no_cm_exception():
    text = " ".join(item.text for item in section_by_id("exam-registration").items)
    assert "7 days before" in text
    assert "48 hours before" in text
    assert "genuinely have no access" in text
    assert "forgetting to book in CM is not this exception" in text


def test_exam_attempts_and_passing_grade_improvement_have_different_conditions():
    section = section_by_id("exam-attempts-and-improvement")
    assert section.items[0].maximum == 4
    assert section.items[1].maximum == 2
    text = section.items[2].text
    assert "take and pass the first possible exam date" in text
    assert "one repeat for grade improvement" in text
    assert "no later than the beginning of the following semester" in text
    assert "better grade counts" in text
    assert "excluded for repeat exams after failure" in text


def test_study_abroad_requires_advance_planning_not_an_app_generated_approval():
    section = section_by_id("study-abroad")
    text = " ".join(item.text for item in section.items)
    assert "Before departure" in text and "Prüfungsausschuss chair" in text
    assert "not itself an approved agreement" in text
    assert "second or third subject semester" in text
    assert "not a restriction to those semesters" in text
