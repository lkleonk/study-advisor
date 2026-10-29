from app.domain.course_offerings import (
    available_semesters,
    get_course_bucket,
    project_offerings,
    validate_course_catalog,
)
from app.domain.degrees import get_degree
from app.services.nodes.scope_classifier import heuristic_classify


PHYSIK = "bsc_physik"


def _section(section_id: str):
    catalogue = get_degree(PHYSIK).get_program_rules()
    return next(section for section in catalogue.sections if section.id == section_id)


def test_physik_rules_match_the_2024_regulation_totals():
    compulsory = _section("compulsory-modules")
    assert sum(item.minimum for item in compulsory.items) == 113

    structure = {item.label: item.minimum for item in _section("kernfach-structure").items}
    assert structure == {"Pflichtbereich": 125, "Wahlpflichtbereich": 25}


def test_physik_offerings_are_valid_and_carry_module_lp():
    validate_course_catalog()

    assert available_semesters(PHYSIK) == ["sose26", "wise26-27"]
    lectures = get_course_bucket(PHYSIK, "wise26-27/compulsory/vl")["courses"]
    quantenmechanik = next(course for course in lectures if course["title"] == "Quantenmechanik")
    assert quantenmechanik["lp"] == 12


def test_physik_tree_uses_only_physik_areas():
    tree = project_offerings(PHYSIK)
    areas = {area for semester in tree.values() for area in semester}
    assert areas <= {"compulsory", "compulsory_elective", "abv"}


def test_physik_has_no_plan_validation():
    assert get_degree(PHYSIK).plan_validation_enabled is False


def test_heuristic_fallback_uses_degree_specific_terms():
    terms = get_degree(PHYSIK).prompts.fallback_domain_terms
    message = "Ist das Physik Grundpraktikum schwer?"

    assert heuristic_classify(message) == "off_topic"
    assert heuristic_classify(message, terms) == "degree_question"
