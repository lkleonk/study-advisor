"""Project canonical course data into degree- and semester-specific lookups.

Course identity lives in ``data/courses.json``. Degree credit mappings live in
``data/degree_modules/<degree>.json`` and semester delivery details live in
``data/course_offerings/<semester>.json``. This keeps shared courses and their
LP values canonical while allowing a course to count differently per degree.
"""

import re
from datetime import date
from functools import lru_cache
from typing import Any
from urllib.parse import urlparse

from app.domain.catalog_data import (
    COURSE_OFFERINGS_DIR,
    course_name,
    load_courses,
    load_degree_module_data,
    module_entries_by_id,
)


LOOKUP_KEY_SEPARATOR = "/"
VALID_COURSE_TYPES = {"vl", "swp", "praktikum", "seminar"}
REQUIRED_OFFERING_FIELDS = {"course_id", "type", "lp", "first_sessions", "url"}
OPTIONAL_OFFERING_FIELDS = {"uebungen", "uebung_url"}
# Sessions are first appointments, never the full timetable. Each one is
# {"date": "YYYY-MM-DD", "start": "HH:MM", "end": "HH:MM", "room": "..."}; date is
# required, start/end come as a pair, room is optional. The weekday is derived.
# first_sessions: the first appointment of each weekly slot of the main
# lecture/seminar (at most MAX_FIRST_SESSIONS). uebungen (lectures only): the first
# appointment of each Übung group; empty while the VV lists none. uebung_url
# (lectures only): VV page of the separate Übung event.
SESSION_FIELDS = {"date", "start", "end", "room"}
MAX_FIRST_SESSIONS = 4
# Above this many Übung groups the chat context gives only the count, not the list.
UEBUNG_CONTEXT_MAX_GROUPS = 8
TIME_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")
WEEKDAYS_EN = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
# Official FU module code of a degree module, e.g. "0086eA1.14" (B.Sc. Informatik).
FU_MODULE_CODE_RE = re.compile(r"^\d{4}[a-z][A-Z]\d+\.\d+$")
# credit_note on a placement: one short sentence on how the course counts for that
# degree (e.g. "free-elective candidate only"). Not a description: no event numbers,
# lecturers, module codes, or times.
CREDIT_NOTE_MAX_LENGTH = 200
CREDIT_NOTE_FORBIDDEN_RE = re.compile(r"\b\d{8}\b|FU module|\b\d{4}[a-z][A-Z]\d+\.\d+\b|\b(?:Mo|Di|Mi|Do|Fr|Sa|So) \d{2}:\d{2}")
# Degree-specific note shown once under an area heading in the Course Registry.
AREA_NOTES = {
    "bsc_informatik": {
        "free_elective": "Candidates only; credit recognition and relevance require confirmation.",
    },
    "bsc_bioinformatik": {
        "wahlbereich": "Examples only; modules other than the recommended ones need Prüfungsausschuss approval.",
    },
}
MARKDOWN_LINK_RE = re.compile(r"^\[[^\]]+\]\((https?://[^)]+)\)$")
SEMESTER_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

COURSE_TYPE_LABELS = {
    "vl": "Lecture",
    "swp": "Software project",
    "praktikum": "Practical course",
    "seminar": "Seminar",
}
AREA_LABELS = {
    "msc_informatik": {
        "practical": "Practical Informatics",
        "theoretical": "Theoretical Informatics",
        "technical": "Technical Informatics",
        "application": "Application Area",
    },
    "msc_data_science": {
        "grundlagen": "Foundations",
        "life_sciences": "Life Sciences",
        "technologies": "Technologies",
    },
    "bsc_informatik": {
        "compulsory": "Compulsory Informatics",
        "compulsory_elective": "Compulsory-elective Informatics",
        "free_elective": "Free elective",
        "abv": "ABV",
    },
    "bsc_physik": {
        "compulsory": "Compulsory Physik",
        "compulsory_elective": "Compulsory-elective Physik",
        "abv": "ABV",
    },
    "bsc_bioinformatik": {
        "informatik": "Informatik/Algorithmische Bioinformatik",
        "mathematik_statistik": "Mathematik/Statistik",
        "biologie_chemie": "Biologie/Chemie/Biochemie",
        "wahlbereich": "Wahlbereich",
        "abv": "ABV",
    },
    "msc_physik": {
        "compulsory": "Compulsory modules",
        "compulsory_elective": "Compulsory-elective (Wahlpflicht)",
        "elective": "Elective area (Wahlbereich)",
        "research_phase": "Research phase",
    },
}


def normalize_course_url(value: Any) -> str | None:
    if value is None or not isinstance(value, str):
        return None
    stripped = value.strip()
    if not stripped:
        return None
    markdown_match = MARKDOWN_LINK_RE.match(stripped)
    url = markdown_match.group(1) if markdown_match else stripped
    parsed = urlparse(url)
    return url if parsed.scheme in {"http", "https"} and parsed.netloc else None


def course_type_label(course_type: str) -> str:
    """Return the display label for a stable course-type ID."""
    return COURSE_TYPE_LABELS.get(course_type, course_type.replace("_", " ").title())


def area_note(degree_id: str, area: str) -> str | None:
    """Return an optional degree-specific note for an area, shown once per area."""
    return AREA_NOTES.get(degree_id, {}).get(area)


def area_label(degree_id: str, area: str) -> str:
    """Return the degree-specific display label for a stable area ID."""
    return AREA_LABELS.get(degree_id, {}).get(area, area.replace("_", " ").title())


def semester_label(semester: str) -> str:
    """Format known semester IDs without rejecting future valid IDs."""
    sose_match = re.fullmatch(r"sose(\d{2}|\d{4})", semester)
    if sose_match:
        return f"SoSe {_semester_year(sose_match.group(1))}"

    wise_match = re.fullmatch(r"wise(\d{2}|\d{4})-(\d{2}|\d{4})", semester)
    if wise_match:
        start, end = (_semester_year(part) for part in wise_match.groups())
        return f"WiSe {start}/{str(end)[-2:]}"

    return semester


def _semester_year(value: str) -> int:
    return int(value) if len(value) == 4 else 2000 + int(value)


def load_course_entries() -> list[dict[str, Any]]:
    """Return flattened semester offerings enriched with canonical course names."""
    return _load_course_entries_cached()


@lru_cache(maxsize=1)
def _load_course_entries_cached() -> list[dict[str, Any]]:
    validate_course_catalog()
    entries: list[dict[str, Any]] = []
    for path in sorted(COURSE_OFFERINGS_DIR.glob("*.json")):
        data = _read_semester_file(path)
        semester = data["semester"]
        for offering in data["offerings"]:
            entries.append({"semester": semester, **offering, "title": course_name(offering["course_id"])})
    return entries


def _read_semester_file(path) -> dict[str, Any]:
    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain an object.")
    semester = data.get("semester")
    if not isinstance(semester, str) or not SEMESTER_RE.match(semester):
        raise ValueError(f"{path.name} has an invalid semester.")
    if path.stem != semester:
        raise ValueError(f"{path.name} must match its semester value {semester!r}.")
    offerings = data.get("offerings")
    if not isinstance(offerings, list) or not offerings:
        raise ValueError(f"{path.name}.offerings must be a non-empty list.")
    return data


def validate_course_catalog() -> None:
    """Validate the three-layer catalogue and all cross-file references."""
    from app.domain.degrees import get_degree, is_valid_degree, list_degrees

    courses = load_courses()
    if not COURSE_OFFERINGS_DIR.exists():
        raise ValueError("course_offerings directory is missing.")

    credit_maps: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for degree_summary in list_degrees():
        degree_id = degree_summary.id
        degree = get_degree(degree_id)
        data = load_degree_module_data(degree_id)
        modules = module_entries_by_id(degree_id)
        credit_map: dict[str, list[dict[str, Any]]] = {}

        for module_id, module in modules.items():
            area = module.get("area")
            if area is not None and area not in {*degree.course_areas, "thesis"}:
                raise ValueError(f"{degree_id} module {module_id!r} has invalid area {area!r}.")
            for flag in ("is_ungraded", "is_bachelor_module", "is_scientific_work", "is_software_project"):
                if flag in module and not isinstance(module[flag], bool):
                    raise ValueError(f"{degree_id} module {module_id!r} {flag} must be a boolean.")
            code = module.get("fu_module_code")
            if code is not None and (not isinstance(code, str) or not FU_MODULE_CODE_RE.fullmatch(code)):
                raise ValueError(f"{degree_id} module {module_id!r} fu_module_code must look like '0086eA1.14'; got {code!r}.")

        mappings = data.get("offering_credits", [])
        if not isinstance(mappings, list):
            raise ValueError(f"{degree_id}.offering_credits must be a list.")
        for mapping in mappings:
            if not isinstance(mapping, dict) or mapping.get("course_id") not in courses:
                raise ValueError(f"{degree_id} credit mapping references an unknown course.")
            course_id = mapping["course_id"]
            if course_id in credit_map:
                raise ValueError(f"{degree_id} duplicates credit mapping for course {course_id!r}.")
            placements = mapping.get("placements")
            if not isinstance(placements, list) or not placements:
                raise ValueError(f"{degree_id} credit mapping {course_id!r} needs placements.")
            seen_areas: set[str] = set()
            for placement in placements:
                if not isinstance(placement, dict) or placement.get("module_id") not in modules:
                    raise ValueError(f"{degree_id} credit mapping {course_id!r} references an unknown module.")
                module = modules[placement["module_id"]]
                area = placement.get("area", module.get("area"))
                if area not in degree.course_areas:
                    raise ValueError(f"{degree_id} credit mapping {course_id!r} has invalid area {area!r}.")
                if area in seen_areas:
                    raise ValueError(f"{degree_id} credit mapping {course_id!r} places area {area!r} twice.")
                seen_areas.add(area)
                if placement.get("lp") is not None and not isinstance(placement["lp"], int):
                    raise ValueError(f"{degree_id} credit mapping {course_id!r} lp must be an integer or null.")
                if "description" in placement:
                    raise ValueError(f"{degree_id} credit mapping {course_id!r} uses removed field 'description'; use credit_note.")
                note = placement.get("credit_note")
                if note is not None and (
                    not isinstance(note, str)
                    or len(note) > CREDIT_NOTE_MAX_LENGTH
                    or CREDIT_NOTE_FORBIDDEN_RE.search(note)
                ):
                    raise ValueError(
                        f"{degree_id} credit mapping {course_id!r} credit_note must be one short sentence about "
                        f"crediting (max {CREDIT_NOTE_MAX_LENGTH} chars, no event numbers, module codes, or times)."
                    )
                if "is_bachelor_module" in placement and not isinstance(placement["is_bachelor_module"], bool):
                    raise ValueError(f"{degree_id} credit mapping {course_id!r} is_bachelor_module must be a boolean.")
            credit_map[course_id] = placements
        credit_maps[degree_id] = credit_map

    seen_entries: set[tuple[str, str, str]] = set()
    for path in sorted(COURSE_OFFERINGS_DIR.glob("*.json")):
        data = _read_semester_file(path)
        semester = data["semester"]
        for index, offering in enumerate(data["offerings"]):
            label = f"{path.name}.offerings[{index}]"
            if not isinstance(offering, dict):
                raise ValueError(f"{label} must be an object.")
            missing = REQUIRED_OFFERING_FIELDS - set(offering)
            if missing:
                raise ValueError(f"{label} misses required fields: {sorted(missing)}")
            extra = set(offering) - REQUIRED_OFFERING_FIELDS - OPTIONAL_OFFERING_FIELDS
            if extra:
                raise ValueError(f"{label} has unsupported fields: {sorted(extra)}")
            course_id = offering["course_id"]
            if course_id not in courses:
                raise ValueError(f"{label} references unknown course id {course_id!r}.")
            if offering.get("type") not in VALID_COURSE_TYPES:
                raise ValueError(f"{label} has invalid course type {offering.get('type')!r}.")
            if offering.get("lp") is not None and not isinstance(offering["lp"], int):
                raise ValueError(f"{label}.lp must be an integer or null.")
            if offering.get("url") is not None and not isinstance(offering["url"], str):
                raise ValueError(f"{label}.url must be a string or null.")
            _validate_sessions(f"{label}.first_sessions", offering["first_sessions"], max_count=MAX_FIRST_SESSIONS)
            if "uebungen" in offering:
                if offering["type"] != "vl":
                    raise ValueError(f"{label}.uebungen is only allowed on lectures (type 'vl').")
                _validate_sessions(f"{label}.uebungen", offering["uebungen"])
            if "uebung_url" in offering:
                if offering["type"] != "vl":
                    raise ValueError(f"{label}.uebung_url is only allowed on lectures (type 'vl').")
                if offering["uebung_url"] is not None and not isinstance(offering["uebung_url"], str):
                    raise ValueError(f"{label}.uebung_url must be a string or null.")
            identity = (semester, offering["type"], course_id)
            if identity in seen_entries:
                raise ValueError(f"{label} duplicates {identity}.")
            seen_entries.add(identity)


def _validate_sessions(label: str, value: Any, *, max_count: int | None = None) -> None:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list of first appointments; got {value!r}.")
    if max_count is not None and len(value) > max_count:
        raise ValueError(f"{label} holds at most {max_count} first appointments; got {len(value)}.")
    for index, session in enumerate(value):
        _validate_session(f"{label}[{index}]", session)
    keys = [(session["date"], session.get("start") or "", session.get("room") or "") for session in value]
    if keys != sorted(set(keys)):
        raise ValueError(f"{label} must be sorted by date, start, and room without duplicates.")


def _validate_session(label: str, value: Any) -> None:
    hint = 'expected {"date": "YYYY-MM-DD", "start": "HH:MM", "end": "HH:MM", "room": "..."} for one first appointment'
    if not isinstance(value, dict) or "date" not in value or set(value) - SESSION_FIELDS:
        raise ValueError(f"{label}: {hint}; got {value!r}.")
    try:
        date.fromisoformat(value["date"])
    except (TypeError, ValueError):
        raise ValueError(f"{label}.date must be YYYY-MM-DD; got {value['date']!r}.") from None
    if ("start" in value) != ("end" in value):
        raise ValueError(f"{label} needs both start and end, or neither.")
    if "start" in value:
        if not all(isinstance(value[k], str) and TIME_RE.fullmatch(value[k]) for k in ("start", "end")):
            raise ValueError(f"{label} start/end must be HH:MM; got {value!r}.")
        if value["start"] >= value["end"]:
            raise ValueError(f"{label} start must be before end; got {value!r}.")
    room = value.get("room")
    if room is not None and (not isinstance(room, str) or not room.strip() or ";" in room):
        raise ValueError(f"{label}.room must be one room name; got {room!r}.")


def format_session(session: dict[str, str]) -> str:
    """Render one weekly slot by its first appointment, e.g. for LLM context."""
    day = date.fromisoformat(session["date"])
    text = WEEKDAYS_EN[day.weekday()]
    if session.get("start"):
        text += f" {session['start']}-{session['end']}"
    text += f" from {day.strftime('%d.%m.%Y')}"
    if session.get("room"):
        text += f" ({session['room']})"
    return text


def _degree_placements(degree_id: str, course_id: str) -> list[dict[str, Any]]:
    data = load_degree_module_data(degree_id)
    for mapping in data.get("offering_credits", []):
        if mapping["course_id"] == course_id:
            return mapping["placements"]
    return []


def project_offerings(degree_id: str) -> dict[str, Any]:
    return _project_offerings_cached(degree_id)


@lru_cache(maxsize=16)
def _project_offerings_cached(degree_id: str) -> dict[str, Any]:
    from app.domain.degrees import get_degree

    degree = get_degree(degree_id)
    modules = module_entries_by_id(degree_id)
    tree: dict[str, Any] = {}
    for offering in load_course_entries():
        for placement in _degree_placements(degree_id, offering["course_id"]):
            module = modules[placement["module_id"]]
            area = placement.get("area", module.get("area"))
            course = {
                "title": offering["title"],
                "module_catalog_name": degree.course_modules[placement["module_id"]],
                "fu_module_code": module.get("fu_module_code"),
                "lp": placement.get("lp") if placement.get("lp") is not None else offering.get("lp"),
                "first_sessions": offering["first_sessions"],
                "uebungen": offering.get("uebungen", []),
                "uebung_url": offering.get("uebung_url"),
                "credit_note": placement.get("credit_note"),
                "url": offering.get("url"),
            }
            if placement.get("is_bachelor_module") or module.get("is_bachelor_module"):
                course["is_bachelor_module"] = True
            bucket = tree.setdefault(offering["semester"], {}).setdefault(area, {}).setdefault(offering["type"], [])
            bucket.append(course)
    return tree


def has_offerings(degree_id: str) -> bool:
    return bool(project_offerings(degree_id))


def lookup_key(semester: str, area: str, course_type: str) -> str:
    return LOOKUP_KEY_SEPARATOR.join([semester, area, course_type])


def parse_lookup_key(key: str) -> tuple[str, str, str]:
    parts = key.split(LOOKUP_KEY_SEPARATOR)
    if len(parts) != 3 or not all(parts):
        raise ValueError(f"Lookup key must use semester/area/course_type format: {key!r}")
    return parts[0], parts[1], parts[2]


def iter_lookup_keys(degree_id: str) -> list[str]:
    return [
        lookup_key(semester, area, course_type)
        for semester, areas in project_offerings(degree_id).items()
        for area, course_types in areas.items()
        for course_type in course_types
    ]


def available_semesters(degree_id: str) -> list[str]:
    return list(project_offerings(degree_id).keys())


def build_available_semesters_note(degree_id: str) -> str:
    semesters = available_semesters(degree_id)
    if not semesters:
        return "Available semesters in local course-offering data: none."
    return (
        "Available semesters in local course-offering data: "
        f"{', '.join(semesters)}. No local course-offering data exists for other semesters."
    )


def available_areas(degree_id: str, semester: str) -> list[str]:
    return list((project_offerings(degree_id).get(semester) or {}).keys())


def available_course_types(degree_id: str, semester: str, area: str) -> list[str]:
    return list(((project_offerings(degree_id).get(semester) or {}).get(area) or {}).keys())


def get_course_bucket(degree_id: str, key: str) -> dict[str, Any] | None:
    semester, area, course_type = parse_lookup_key(key)
    courses = ((project_offerings(degree_id).get(semester) or {}).get(area) or {}).get(course_type)
    if courses is None:
        return None
    return {"key": key, "semester": semester, "area": area, "course_type": course_type, "courses": [_normalized_course(course) for course in courses]}


def lookup_course_buckets(degree_id: str, keys: list[str]) -> tuple[list[dict[str, Any]], list[str]]:
    buckets: list[dict[str, Any]] = []
    invalid_keys: list[str] = []
    for key in dict.fromkeys(keys):
        try:
            bucket = get_course_bucket(degree_id, key)
        except ValueError:
            bucket = None
        if bucket is None:
            invalid_keys.append(key)
        else:
            buckets.append(bucket)
    return buckets, invalid_keys


def build_course_lookup_tree(degree_id: str) -> str:
    lines = ["Available course-offering lookup tree. Only output keys shown after ->."]
    for semester, areas in project_offerings(degree_id).items():
        lines.append(semester)
        for area, course_types in areas.items():
            lines.append(f"  {area}")
            for course_type, courses in course_types.items():
                key = lookup_key(semester, area, course_type)
                sample_titles = [str(course["title"]).strip() for course in courses[:3] if str(course["title"]).strip()]
                sample = f": {', '.join(sample_titles)}" if sample_titles else ""
                lines.append(f"    {course_type} -> {key} ({len(courses)} course(s){sample})")
    return "\n".join(lines)


def format_course_lookup_context(
    buckets: list[dict[str, Any]],
    invalid_keys: list[str] | None = None,
    notes: list[str] | None = None,
    *,
    include_course_urls: bool = True,
) -> str:
    parts = ["Exact local course offerings from the canonical course catalogue and semester data."]
    parts.extend(f"Note: {note}" for note in notes or [] if note)
    if invalid_keys:
        parts.append("No local course-offering bucket exists for these requested keys: " + ", ".join(invalid_keys))
    for bucket in buckets:
        lines = [
            f"## {bucket['key']}", f"Semester: {bucket['semester']}", f"Area: {bucket['area']}",
            f"Course type: {bucket['course_type']}", f"Grading hint: {_grading_hint(bucket['course_type'])}",
            f"Courses listed: {len(bucket['courses'])}",
        ]
        for index, course in enumerate(bucket["courses"], start=1):
            lines.extend(_format_course(index, course, bucket["course_type"], include_course_url=include_course_urls))
        parts.append("\n".join(lines))
    return "" if len(parts) == 1 else "\n\n".join(parts)


def build_course_citations(
    buckets: list[dict[str, Any]],
    *,
    include_course_urls: bool = True,
) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []
    seen: set[tuple[str, str | None, str | None]] = set()
    for bucket in buckets:
        source = f"backend/app/domain/data/course_offerings/{bucket['semester']}.json"
        _append_unique_citation(citations, seen, {"source": source, "title": "Course offerings", "section_heading": bucket["key"], "page": None, "score": 1.0})
        if include_course_urls:
            for course in bucket["courses"]:
                url = normalize_course_url(course.get("url"))
                if url:
                    _append_unique_citation(citations, seen, {"source": url, "title": course.get("title"), "section_heading": bucket["key"], "page": None, "score": 1.0})
    return citations


def _append_unique_citation(citations: list[dict[str, Any]], seen: set[tuple[str, str | None, str | None]], citation: dict[str, Any]) -> None:
    identity = (citation["source"], citation.get("title"), citation.get("section_heading"))
    if identity not in seen:
        seen.add(identity)
        citations.append(citation)


def _normalized_course(course: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(course)
    normalized["url"] = normalize_course_url(course.get("url"))
    if course.get("uebung_url"):
        normalized["uebung_url"] = normalize_course_url(course["uebung_url"])
    return normalized


def _format_course(
    index: int,
    course: dict[str, Any],
    course_type: str,
    *,
    include_course_url: bool = True,
) -> list[str]:
    lp = course.get("lp") if course.get("lp") is not None else "not listed in offerings data"
    lines = [f"{index}. Title: {course.get('title')}", f"   Module catalog name: {course.get('module_catalog_name')}"]
    if course.get("fu_module_code"):
        lines.append(f"   FU module code: {course['fu_module_code']}")
    lines.append(f"   LP: {lp}")
    if course.get("is_bachelor_module"):
        lines.append("   Bachelor module: counts toward the maximum of 15 LP of Bachelor modules in a Master plan.")
    if course.get("first_sessions"):
        sessions = "; ".join(format_session(session) for session in course["first_sessions"])
        lines.append(f"   Sessions (weekly): {sessions}")
    if course_type == "vl":
        groups = course.get("uebungen") or []
        if not groups:
            lines.append("   Übung: no data")
        elif len(groups) > UEBUNG_CONTEXT_MAX_GROUPS:
            lines.append(f"   Übung: {len(groups)} groups (times not listed here)")
        else:
            lines.append(f"   Übung groups (weekly): {'; '.join(format_session(group) for group in groups)}")
        if include_course_url and course.get("uebung_url"):
            lines.append(f"   Übung URL: {course['uebung_url']}")
    if course.get("credit_note"):
        lines.append(f"   Credit note: {course['credit_note']}")
    if include_course_url and course.get("url"):
        lines.append(f"   URL: {course['url']}")
    return lines


def _grading_hint(course_type: str) -> str:
    if course_type == "vl":
        return "Vorlesung module; treat as graded for advisory answers."
    if course_type == "seminar":
        return "Seminar/Wissenschaftliches Arbeiten; treat as ungraded for advisory answers."
    if course_type == "swp":
        return "Softwareprojekt A is graded and Softwareprojekt B is ungraded; use the module catalog name when present."
    if course_type == "praktikum":
        return "Practical-course offering; consult the module details for assessment information."
    return "No grading hint available."
