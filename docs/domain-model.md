# Domain Model

How degrees, course-offering data, and program rules fit together. Per-degree
validation specifics for M.Sc. Data Science live in `docs/data_science_master.md`;
the enumerated rule lists live in each degree's `degree_rules.py` (the code is
the source of truth — do not restate the lists here).

## Degree registry

`backend/app/domain/degrees/__init__.py` maps degree ids to `DegreeDefinition`
instances (`definition.py`). Every session is bound to exactly one degree; the
LLM never chooses or infers it. Currently registered: `msc_informatik`
(M.Sc. Informatik, SPO 2014), `msc_data_science` (M.Sc. Data Science,
FU-Mitteilungen 18/2021), `bsc_informatik` (B.Sc. Informatik,
FU-Mitteilungen 23/2023), `bsc_physik` (B.Sc. Physik Monobachelor,
FU-Mitteilungen 12/2024), `msc_physik` (M.Sc. Physik, FU-Mitteilungen
12/2024), and `bsc_bioinformatik` (B.Sc. Bioinformatik, FU-Mitteilungen
34/2023). Both Physik degrees have a rules catalogue, module list, and SoSe 2026 /
WiSe 2026/27 offerings, without plan validation. B.Sc. Bioinformatik is a joint
FU/Charité programme; its areas follow the regulation's three study areas
(`informatik`, `mathematik_statistik`, `biologie_chemie`) plus `wahlbereich` and
`abv`. It reuses the shared B.Sc. Informatik courses (for example Konzepte der
Programmierung), and the Wahlbereich and free ABV each hold one placeholder module
with example offerings, not an approved list. No plan validation. The B.Sc. package provides its 2023 programme-rules
catalogue and the locally supplied SoSe 2026 and WiSe 2026/27 offering
projections. Its deterministic study-plan validation remains unavailable. The
B.Sc. projection does not imply that modules are offered in other semesters;
its 0084d maths entries are free-elective candidates only and still require
recognition and relevance confirmation.

Each degree package owns:

```text
prompts.py         -> DegreePromptSpec: degree-specific prompt vocabulary/overrides
degree_rules.py    -> deterministic validate_study_plan()
program_rules.py   -> structured display catalogue (shared models from app.domain.program_rules)
module_catalog.py  -> canonical module list (checklist-style degrees only)
__init__.py        -> assembles the DegreeDefinition
```

Prompt text itself is shared: `domain/degrees/prompt_builder.py` renders every
`DegreePrompts` from a degree's `SPEC` via `build_prompts()`; the composer's
plan-check wording follows `plan_validation_enabled`. Degrees without their own
parser schema use `GENERIC_STUDY_PLAN_SCHEMA` (`thesis`/`unknown` areas).

`plan_validation_enabled` (default `False`) marks degrees whose deterministic
validator is trusted; only `msc_informatik` sets it. The other validators stay
in the code and tests but are not used at runtime until the flag is flipped.

`DegreeDefinition` fields beyond prompts/rules: `study_plan_schema` (parser LLM
output schema), `enrich_study_plan` (deterministic post-parse enrichment),
`course_areas` (area vocabulary for course-offering placements), and
`course_modules` (canonical id -> display name map).

Validation styles differ by degree and should stay per-degree functions behind
the common interface, not a generic rule engine:

- `msc_informatik`: LP arithmetic over separate credit allocations plus flags
  (specialization minimums, whole-plan seminar/project caps, grading and
  Bachelor-level limits, prior-credit reuse, incompatible management modules).
- `msc_data_science`: checklist matching against the canonical module list; the
  profile (Life Sciences vs Technologies) is inferred from its mandatory marker
  modules, never declared by the LLM.

**Adding a degree:** create the package (a `prompts.py` `SPEC`, `program_rules.py`,
`degree_rules.py`, `__init__.py`; `bsc_physik` is the smallest template), add
`degree_modules/<degree>.json` and offerings, register it in `_DEGREES`, add its
area labels to `AREA_LABELS` in `course_offerings.py`, add it to
`FALLBACK_DEGREES` in the frontend `DegreeContext`, and add focused tests. The
API, frontend picker, and course-offering validation pick it up from the registry.

## Course-offering data

The catalogue has three layers:

```text
backend/app/domain/data/courses.json                     # shared course identity/name/LP/aliases
backend/app/domain/data/degree_modules/<degree>.json     # degree credit mappings and validation flags
backend/app/domain/data/course_offerings/<semester>.json # type, first_sessions, uebungen, URL
```

Each course has one global ID, even if it appears in only one known semester.
Degree mappings state how that course is creditable for a particular regulation;
an offering file records only its semester-specific delivery details:

```json
{
  "course_id": "telematik",
  "type": "vl",
  "lp": 10,
  "first_sessions": [
    {"date": "2026-10-12", "start": "14:00", "end": "16:00", "room": "A7/SR 031 (Arnimallee 7)"},
    {"date": "2026-10-15", "start": "16:00", "end": "18:00", "room": "A7/SR 031 (Arnimallee 7)"}
  ],
  "uebungen": [
    {"date": "2026-10-13", "start": "14:00", "end": "16:00", "room": "T9/SR 006 Seminarraum (Takustr. 9)"}
  ],
  "uebung_url": "https://www.fu-berlin.de/vv/de/lv/1117583?sm=1039762",
  "url": null
}
```

Cross-file invariants, enforced at load time by
`app.domain.course_offerings.validate_course_catalog` (and guarded by
`tests/domain/test_course_offerings.py::test_real_catalogue_is_valid`):

- IDs must resolve across all three layers.
- Credit mappings must use a known degree module and one of that degree's areas.
- A course may map to multiple modules/areas within one degree.
- Placement-level LP is the LP of the module the course is credited to (e.g.
  5 LP for a topic lecture under "Aktuelle Forschungsthemen", 10 LP for a
  Softwareprojekt). It wins over offering-level LP. B.Sc. "Wissenschaftliches
  Arbeiten" lecture/proseminar placements stay without LP because they are
  parts of one 6-LP module.
- Offering-level LP remains a semester-specific override when the delivery
  differs from the canonical module LP.
- Bachelor-module markers remain part of degree credit mappings so the lookup
  context renders the 15 LP cap caveat.
- Sessions are **first appointments**, never the timetable: each is an object
  `{date: YYYY-MM-DD, start?: HH:MM, end?: HH:MM, room?: string}` (start/end as a
  pair; the weekday is derived from the date).
  - `first_sessions` (required): the first appointment of each weekly slot of the
    main lecture/seminar, at most four (e.g. Mo + Do). `[]` when the VV lists no date.
  - `uebungen` (lectures only, optional): the first appointment of each Übung
    group, taken from the separate Übung event in the VV (e.g. "Übung zu
    Telematik"). `[]` while the VV lists none; every lecture is assumed to have an
    Übung, so an empty list means "not published yet": the card shows nothing,
    the chat context says `Übung: no data`. Tutor meetings (Tutorenbesprechung)
    are not groups. Above `UEBUNG_CONTEXT_MAX_GROUPS` (8) groups the chat context
    gives only the group count; the card always lists all groups.
  - `uebung_url` (lectures only, optional): VV page of the Übung event.
  - Both lists are sorted by date/start without duplicates. The validator rejects
    extra keys, non-ISO dates, half time ranges, and room text containing `;`.
- There is no free-text description field. Each fact has its own field:
  - `fu_module_code` on a **module entry** in `degree_modules/<degree>.json`: the
    official FU module code of that module in that regulation (e.g. `0086eA1.14`),
    `null`/absent if unknown. The Course Registry shows it after the module name.
  - `credit_note` on a **placement**: one short sentence on how the course counts
    for that degree (e.g. "free-elective candidate only"). Max 200 characters, no
    event numbers, module codes, lecturers, or times. Used in chat context only,
    not shown on cards.
  - Event numbers and lecturers are not stored; the VV `url` covers them.
- `AREA_NOTES` in `course_offerings.py` holds an optional note shown once under an
  area heading (e.g. the B.Sc. Informatik free-elective caveat).

`project_offerings(degree_id)` builds the per-degree
`semester -> area -> course_type` bucket tree deterministically; the LLM
course-key selector only ever sees the tree for the session's degree.
`tests/fixtures/msc_informatik_buckets_pre_migration.json` pins the projected
SoSe 2026 Master tree to the pre-migration bucket file.

Semester files are curated from the FU Vorlesungsverzeichnis per degree. Only
courses creditable to one of the degree's modules are included: the M.Sc.
listing also contains the whole mathematics tree (Analysis III, Numerik,
Topologie, BMS seminars, ...), which is deliberately left out. Übungen are not
separate offerings; their groups live in the lecture's `uebungen`.

Offering URLs remain in the semester source data and projected Course Registry
API. Their exposure through the agent lookup is separately controlled by
`AGENT_COURSE_LOOKUP_INCLUDE_COURSE_URLS` (default `false`): when disabled,
course lookup omits individual URL lines from `course_context` and omits
URL-based citations while retaining bucket/source citations.

## Program rules catalogue

Structured display rules live per degree:

```text
backend/app/domain/program_rules.py                  # shared models + render_rules_context()
backend/app/domain/degrees/<degree>/program_rules.py # per-degree catalogue content
```

Purpose:

- Source for the frontend Degree Rules tab (selected via `?degree=`).
- Human-readable catalogue of degree-rule sections, items, sources, and related
  validation issue codes.
- Stable JSON projection through `GET /api/program-rules`.

The frontend calls the API and renders structured JSON; it must not own or
duplicate degree-rule validation.

### Ownership split

```text
degrees/<d>/degree_rules.py       -> executable validation logic
degrees/<d>/program_rules.py      -> structured human-readable rule catalogue
services/nodes/answer_composer.py -> filtered prompt context rendered from the degree catalogue
data/courses.json                 -> shared canonical course facts
data/degree_modules/<d>.json      -> degree-specific credit mappings and validation metadata
data/course_offerings/<term>.json -> semester-specific delivery data
frontend/services/api             -> API client only, no validation-rule ownership
```

When rule behavior changes, update in the affected degree package, in order:

1. `degree_rules.py`
2. `program_rules.py`
3. focused tests (`test_rule_checker.py` for msc_informatik,
   `test_data_science_rules.py` for msc_data_science)

For msc_informatik, validation and display rules use four separate allocations:
70 LP Informatik, 10 LP Anwendungsbereich, 10 LP Wahlbereich, and 30 LP thesis.
`is_wahlbereich` is separate from `area`: a technical module placed in
Wahlbereich retains its subject but contributes only to Wahlbereich, not the
Informatik total or specialization minima. Seminar/project maxima apply across
the whole plan; Wahlbereich does not increase them. The catalogue presents the
four degree components first and then the cross-cutting restrictions, with
public links to the SPO, checklist, and examination-board guidance.

The always-included `checklist-planning` catalogue section explains courses vs.
module slots, checking dedicated named modules before broad topic modules,
preserving flexible slots for future courses, and proposing recognition of
external courses against learning outcomes and workload. Its subject-specific
slot lists are generated from `courses.json` and the M.Sc. Informatik module
mappings, so the UI, copied rules, and composer see the same canonical names and
LP. A slot can have many eligible course alternatives without becoming reusable
multiple times. The list is not a semester offering projection or an automatic
recognition decision; the Prüfungsausschuss decides external equivalence.

The catalogue also includes the always-available advisory sections
`module-rebooking`, `professional-experience`, `exam-registration`,
`exam-attempts-and-improvement`, and `study-abroad` (catalogue v3). They distinguish
planning from rebooking completed modules, describe case-by-case professional
work recognition and its enrollment-period exclusion, explain separate course
and exam registration plus retake/improvement rules, and recommend advance
study-abroad agreements. Sources are the SPO (§§10, 13) and the exam-board page,
including its 31 October 2025 work-recognition clarification.

These sections provide reference guidance to the UI, copied rules, and composer;
they have no deterministic issue codes. The current plan schema lacks completion
records, actual grades and exam attempts, employment/enrollment intervals,
registrations, and recognition/agreement decisions. An arithmetic pass therefore
cannot authorize rebooking, recognize a job, verify exam eligibility, or approve
a study-abroad mapping.

`is_bachelor_module` describes module level. Student-specific prior use is
separate: `counted_in_bachelor` and `used_for_master_admission` are nullable
booleans on `PlannedModule`. Confirmed reuse is an error even for Master-level
modules. Unknown history on Bachelor-level modules produces a warning; catalogue
metadata cannot establish an individual student's eligibility. Surplus credits
outside the Bachelor degree (normally 180 LP) are candidates only when not used
for admission; the 15 LP Bachelor-level cap and recognition requirements remain.

## Study-plan validation principle

```text
LLM parses -> Python validates -> LLM explains
```

The LLM may parse and explain, but must not be trusted for final LP validation.
Shared deterministic code:

```text
backend/app/domain/study_plan.py    # shared StudyPlan/PlannedModule models
backend/app/domain/rule_check.py    # shared RuleIssue/RuleCheckResult
backend/app/domain/module_catalog.py # Master enrichment + shared normalize_module_name
```

See `docs/study-plan-data.md` for the schemas and data flow.
