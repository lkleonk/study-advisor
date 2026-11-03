from app.domain.catalog_data import course_lp, module_entries_by_id
from app.domain.course_offerings import available_semesters, project_offerings, validate_course_catalog
from app.domain.degrees import get_degree


COMPUTATIONAL_SCIENCES = "msc_computational_sciences"


def _section(section_id: str):
    catalogue = get_degree(COMPUTATIONAL_SCIENCES).get_program_rules()
    return next(section for section in catalogue.sections if section.id == section_id)


def test_rules_match_the_2025_regulation_totals():
    structure = {item.label: item.minimum for item in _section("overall-structure").items if item.minimum}
    assert structure == {
        "Total degree volume": 120,
        "Synchronisierungsbereich": 30,
        "Bereich Scientific Computing": 30,
        "Spezialisierungsbereich": 30,
        "Masterarbeit": 30,
    }

    for section_id in (
        "specialisation-molecular-sciences",
        "specialisation-geosciences",
        "specialisation-atmospheric-sciences",
    ):
        offers = [item for item in _section(section_id).items if item.label.startswith("Angebot")]
        assert sum(item.minimum for item in offers) <= 30 <= sum(item.maximum for item in offers)


def test_scientific_computing_offers_each_topic_as_ungraded_a_and_graded_b():
    modules = module_entries_by_id(COMPUTATIONAL_SCIENCES)
    a_variants = {mid[:-2] for mid, m in modules.items() if m["area"] == "scientific_computing_a"}
    b_variants = {mid[:-2] for mid, m in modules.items() if m["area"] == "scientific_computing_b"}

    assert a_variants == b_variants and len(a_variants) == 13
    for topic in a_variants:
        assert modules[f"{topic}_a"]["is_ungraded"] is True
        assert modules[f"{topic}_b"]["is_ungraded"] is False
        assert course_lp(f"{topic}_a") == course_lp(f"{topic}_b") == 15


def test_double_master_comes_from_the_2026_amendment():
    section = _section("double-degree")
    assert "EUMaster4HPC" in section.title
    assert all("27/2026" in source.label for source in section.sources)


def test_offerings_are_valid_and_degree_scoped():
    validate_course_catalog()

    assert available_semesters(COMPUTATIONAL_SCIENCES) == ["sose26", "wise26-27"]
    areas = {area for semester in project_offerings(COMPUTATIONAL_SCIENCES).values() for area in semester}
    assert areas <= set(get_degree(COMPUTATIONAL_SCIENCES).course_areas)


def test_has_no_plan_validation():
    assert get_degree(COMPUTATIONAL_SCIENCES).plan_validation_enabled is False
