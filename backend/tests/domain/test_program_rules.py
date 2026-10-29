from fastapi.testclient import TestClient

from app.domain.degrees.msc_informatik.program_rules import get_program_rules
from app.domain.degrees import get_degree
from app.domain.program_rules import CROSS_UNIVERSITY_RULE_SECTION_ID, render_rules_context
from app.main import app


def section_by_id(section_id: str):
    catalogue = get_program_rules()
    return next(section for section in catalogue.sections if section.id == section_id)


def test_program_rules_include_softwareprojekt_wahlbereich_caveat():
    section = section_by_id("softwareprojekt")
    text = " ".join(item.text for item in section.items)

    assert "Wahlbereich" in text
    assert "3 Softwareprojekt modules total" in text
    assert "software_project_count" in section.related_issue_codes


def test_program_rules_include_scientific_work_wahlbereich_caveat():
    section = section_by_id("wissenschaftliches-arbeiten")
    text = " ".join(item.text for item in section.items)

    assert "Up to 2 additional Wissenschaftliches Arbeiten modules" in text
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
    }


def test_rules_context_is_rendered_from_program_rules():
    rules_context = render_rules_context(get_program_rules())

    assert "FU Berlin Master Informatik" in rules_context
    assert "COURSES AT HU BERLIN AND TU BERLIN" in rules_context


def test_rules_context_includes_softwareprojekt_wahlbereich_caveat():
    rules_context = render_rules_context(get_program_rules())

    assert "At least 1 and at most 2 core Softwareprojekt modules are required." in rules_context
    assert "allowing 3 Softwareprojekt modules total" in rules_context


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
