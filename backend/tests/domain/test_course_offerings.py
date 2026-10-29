import json
from pathlib import Path

from app.domain.catalog_data import COURSES_PATH, COURSE_OFFERINGS_DIR, DEGREE_MODULES_DIR, load_courses
from app.domain.course_offerings import (
    build_available_semesters_note,
    build_course_citations,
    build_course_lookup_tree,
    format_course_lookup_context,
    get_course_bucket,
    has_offerings,
    iter_lookup_keys,
    normalize_course_url,
    project_offerings,
    validate_course_catalog,
)


MSC = "msc_informatik"
FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "msc_informatik_buckets_pre_migration.json"


def test_catalogue_uses_shared_courses_degree_mappings_and_semester_files():
    courses = load_courses()
    info = json.loads((DEGREE_MODULES_DIR / "msc_informatik.json").read_text(encoding="utf-8"))
    sose26 = json.loads((COURSE_OFFERINGS_DIR / "sose26.json").read_text(encoding="utf-8"))

    assert courses["telematik"]["name"] == "Telematik"
    assert any(module["course_id"] == "telematik" for module in info["modules"])
    assert any(offering["course_id"] == "softwareprojekt_telematik" for offering in sose26["offerings"])
    assert COURSES_PATH.exists()


def test_real_catalogue_is_valid():
    validate_course_catalog()


def test_course_offerings_loads_path_like_lookup_keys():
    keys = iter_lookup_keys(MSC)

    assert "sose26/technical/swp" in keys
    assert "sose26/practical/seminar" in keys
    assert all("::" not in key for key in keys)


def test_available_semesters_note_is_derived_from_offerings():
    note = build_available_semesters_note(MSC)

    assert "sose26" in note
    assert "No local course-offering data exists for other semesters." in note


def test_course_lookup_tree_shows_bucket_keys_and_examples():
    tree = build_course_lookup_tree(MSC)

    assert "sose26" in tree
    assert "swp -> sose26/technical/swp" in tree
    assert "Softwareprojekt: Telematik" in tree


def test_course_lookup_context_contains_whole_bucket():
    bucket = get_course_bucket(MSC, "sose26/technical/swp")

    context = format_course_lookup_context([bucket])

    assert "## sose26/technical/swp" in context
    assert "Softwareprojekt: Telematik" in context
    assert "Softwareprojekt A is graded and Softwareprojekt B is ungraded" in context


def test_course_lookup_context_can_hide_course_urls():
    bucket = get_course_bucket(MSC, "sose26/practical/vl")

    context_with_urls = format_course_lookup_context([bucket], include_course_urls=True)
    context_without_urls = format_course_lookup_context([bucket], include_course_urls=False)

    assert "   URL: https://" in context_with_urls
    assert "   URL: https://" not in context_without_urls
    assert "Bildverarbeitung" in context_without_urls


def test_markdown_style_urls_are_normalized_for_citations():
    assert normalize_course_url("[https://example.test/course](https://example.test/course)") == "https://example.test/course"

    bucket = get_course_bucket(MSC, "sose26/practical/vl")
    citations = build_course_citations([bucket])

    assert any(citation["source"].startswith("https://") for citation in citations)
    assert all(not citation["source"].startswith("[") for citation in citations)
    assert any(citation["source"].endswith("course_offerings/sose26.json") for citation in citations)


def test_course_citations_can_hide_course_urls():
    bucket = get_course_bucket(MSC, "sose26/practical/vl")

    citations = build_course_citations([bucket], include_course_urls=False)

    assert not any(citation["source"].startswith("https://") for citation in citations)
    assert any(citation["source"].endswith("course_offerings/sose26.json") for citation in citations)


def test_data_science_offerings_are_projected():
    assert has_offerings("msc_data_science")
    tree = project_offerings("msc_data_science")
    assert set(tree) == {"sose26", "wise26-27"}
    assert set(tree["sose26"]) == {"grundlagen", "life_sciences", "technologies"}

    def titles(area, course_type):
        return {course["title"] for course in tree["sose26"].get(area, {}).get(course_type, [])}

    # Cross-area elective lecture appears in both profile areas.
    assert "Markovketten" in titles("life_sciences", "vl")
    assert "Markovketten" in titles("technologies", "vl")
    # Named Technologies modules land in the technologies area.
    assert "Datenbanksysteme Data Science" in titles("technologies", "vl")
    assert "sose26" in build_available_semesters_note("msc_data_science")


def test_projection_matches_pre_migration_master_buckets():
    old = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    projected = project_offerings(MSC)

    def bucket_index(tree):
        return {
            (semester, area, course_type): courses
            for semester, areas in tree.items()
            for area, course_types in areas.items()
            for course_type, courses in course_types.items()
        }

    old_buckets = bucket_index(old)
    # The fixture only covers SoSe 2026; later semesters are added on top.
    new_buckets = {key: courses for key, courses in bucket_index(projected).items() if key[0] == "sose26"}
    assert set(new_buckets) == set(old_buckets)

    # Sessions and description are excluded: the fixture predates the
    # first-appointment format and the removal of free-text descriptions.
    def comparable(course, lp=None):
        return (
            course["title"],
            course["module_catalog_name"],
            course.get("lp") if lp is None else lp,
            course.get("url"),
        )

    for key, old_courses in old_buckets.items():
        new_courses = new_buckets[key]
        # The fixture predates module-LP backfill: where it had no LP, accept the projected one.
        new_lp = {(c["title"], c["module_catalog_name"]): c.get("lp") for c in new_courses}
        expected = [
            comparable(c, new_lp.get((c["title"], c["module_catalog_name"])) if c.get("lp") is None else None)
            for c in old_courses
        ]
        assert sorted(expected, key=str) == sorted(map(comparable, new_courses), key=str), key


def test_sessions_hold_only_first_appointments():
    import pytest

    from app.domain.course_offerings import _validate_sessions, format_session

    monday = {"date": "2026-10-12", "start": "10:00", "end": "12:00", "room": "0.3.12 Großer Hörsaal (Arnimallee 14)"}
    wednesday = {"date": "2026-10-14", "start": "10:00", "end": "12:00"}
    _validate_sessions("x", [])
    _validate_sessions("x", [monday, wednesday], max_count=2)
    _validate_sessions("x", [{"date": "2026-04-15"}])
    assert format_session(monday) == "Mon 10:00-12:00 from 12.10.2026 (0.3.12 Großer Hörsaal (Arnimallee 14))"
    # Timetable strings, extra keys, half time ranges, multi-room text, too many
    # lecture slots, and unsorted or duplicate sessions are rejected.
    for bad, max_count in (
        ("Mo 10:00-12:00, Mi 09:00-11:00; Erster Termin: 12.10.2026", None),
        ([{"date": "2026-10-12", "uebung": "Mo 14:00-16:00"}], None),
        ([{"date": "12.10.2026"}], None),
        ([{"date": "2026-10-12", "start": "10:00"}], None),
        ([{"date": "2026-10-12", "room": "Hörsaal; Übung: SR 005"}], None),
        ([monday, wednesday, {"date": "2026-10-16"}], 2),
        ([wednesday, monday], None),
        ([monday, monday], None),
    ):
        with pytest.raises(ValueError):
            _validate_sessions("x", bad, max_count=max_count)


def test_credit_note_rejects_description_dumps():
    from app.domain.course_offerings import CREDIT_NOTE_FORBIDDEN_RE, FU_MODULE_CODE_RE

    assert not CREDIT_NOTE_FORBIDDEN_RE.search("Listed as a free-elective candidate only; recognition requires confirmation.")
    assert CREDIT_NOTE_FORBIDDEN_RE.search("FU module 0086eA1.14. Vorlesung 19335601 (Erika Mustermann).")
    assert CREDIT_NOTE_FORBIDDEN_RE.search("Tutorium: Mo 12:00-14:00")
    assert FU_MODULE_CODE_RE.fullmatch("0086eA1.14") and FU_MODULE_CODE_RE.fullmatch("0590bB2.9")
    assert not FU_MODULE_CODE_RE.fullmatch("FU module 0086eA1.14")


def test_lecture_context_lists_few_uebung_groups_and_counts_many():
    from app.domain.course_offerings import UEBUNG_CONTEXT_MAX_GROUPS, _format_course

    group = {"date": "2026-10-13", "start": "14:00", "end": "16:00"}
    course = {"title": "X", "module_catalog_name": "Y", "lp": 5, "first_sessions": [], "uebungen": []}

    assert "   Übung: no data" in _format_course(1, course, "vl")
    assert not any("Übung" in line for line in _format_course(1, course, "seminar"))
    few = _format_course(1, {**course, "uebungen": [group]}, "vl")
    assert "   Übung groups (weekly): Tue 14:00-16:00 from 13.10.2026" in few
    many = _format_course(1, {**course, "uebungen": [group] * (UEBUNG_CONTEXT_MAX_GROUPS + 1)}, "vl")
    assert f"   Übung: {UEBUNG_CONTEXT_MAX_GROUPS + 1} groups (times not listed here)" in many
