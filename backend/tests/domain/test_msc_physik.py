from app.domain.course_offerings import available_semesters, project_offerings, validate_course_catalog
from app.domain.degrees import get_degree


PHYSIK = "msc_physik"


def _section(section_id: str):
    catalogue = get_degree(PHYSIK).get_program_rules()
    return next(section for section in catalogue.sections if section.id == section_id)


def test_msc_physik_rules_match_the_2024_regulation_totals():
    structure = {item.label: item.minimum for item in _section("overall-structure").items if item.minimum}
    assert structure == {"Total degree volume": 120, "Studienphase": 60, "Angeleitete Forschungsphase": 60}

    assert sum(item.minimum for item in _section("compulsory-modules").items) == 15
    assert _section("compulsory-elective-modules").items[0].minimum == 20
    assert _section("elective-area").items[0].minimum == 25


def test_msc_physik_offerings_are_valid_and_degree_scoped():
    validate_course_catalog()

    assert available_semesters(PHYSIK) == ["sose26", "wise26-27"]
    areas = {area for semester in project_offerings(PHYSIK).values() for area in semester}
    assert areas <= {"compulsory", "compulsory_elective", "elective", "research_phase"}


def test_msc_physik_has_no_plan_validation():
    assert get_degree(PHYSIK).plan_validation_enabled is False
