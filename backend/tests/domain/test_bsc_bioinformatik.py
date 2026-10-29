from app.domain.course_offerings import (
    available_semesters,
    get_course_bucket,
    project_offerings,
    validate_course_catalog,
)
from app.domain.degrees import get_degree
from app.services.nodes.scope_classifier import heuristic_classify


BIOINFORMATIK = "bsc_bioinformatik"


def _section(section_id: str):
    catalogue = get_degree(BIOINFORMATIK).get_program_rules()
    return next(section for section in catalogue.sections if section.id == section_id)


def test_bioinformatik_rules_match_the_2023_regulation_totals():
    assert sum(item.minimum for item in _section("informatik-modules").items) == 46
    assert sum(item.minimum for item in _section("mathematik-statistik-modules").items) == 39
    assert sum(item.minimum for item in _section("biologie-chemie-modules").items) == 47

    structure = {item.label: item.minimum for item in _section("kernfach-structure").items}
    assert sum(structure.values()) == 150


def test_bioinformatik_offerings_are_valid_and_carry_module_lp():
    validate_course_catalog()

    assert "wise26-27" in available_semesters(BIOINFORMATIK)
    lectures = get_course_bucket(BIOINFORMATIK, "wise26-27/informatik/vl")["courses"]
    algbioinf = next(course for course in lectures if course["title"] == "Algorithmische Bioinformatik I und Numerik")
    assert algbioinf["lp"] == 5
    assert algbioinf["uebungen"]


def test_bioinformatik_reuses_shared_informatik_offerings():
    lectures = get_course_bucket(BIOINFORMATIK, "wise26-27/informatik/vl")["courses"]
    assert any(course["title"] == "Konzepte der Programmierung" for course in lectures)


def test_bioinformatik_tree_uses_only_its_areas():
    tree = project_offerings(BIOINFORMATIK)
    areas = {area for semester in tree.values() for area in semester}
    assert areas <= set(get_degree(BIOINFORMATIK).course_areas)


def test_bioinformatik_has_no_plan_validation():
    assert get_degree(BIOINFORMATIK).plan_validation_enabled is False


def test_heuristic_fallback_uses_degree_specific_terms():
    terms = get_degree(BIOINFORMATIK).prompts.fallback_domain_terms
    message = "Wann muss ich das Berufspraktikum machen?"

    assert heuristic_classify(message, terms) == "degree_question"
