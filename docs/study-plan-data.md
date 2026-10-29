# Study Plan Data

This document describes how the FU Berlin CS consultant currently represents, stores, and validates a student's study-program data.

## Current Storage Model

Phase 1 does not persist study-plan data to disk or a database.

The backend uses LangGraph `MemorySaver` in `backend/app/services/agent_graph_service.py`. A session is identified by `session_id`, and that ID is passed to LangGraph as:

```python
config = {"configurable": {"thread_id": session_id}}
```

The graph state for that thread holds:

```text
messages
wizardflow_message_id
message_type
course_lookup_keys
course_lookup_needs_clarification
course_context
citations
parsed_study_plan
rule_check_result
reply
```

Important implications:

- The study plan is in memory only.
- The study plan is lost when the backend process restarts.
- Sessions are deleted after 48 hours of inactivity by opportunistic cleanup
  during later message or transcript requests.
- `DELETE /api/sessions/{session_id}` immediately removes inactive session
  state. If a request for that session is still running, deletion is deferred
  until the active request finishes.
- The current design is not multi-instance safe.
- WizardFlow writes a local diagnostic trace, but there is no authoritative
  study-plan audit database. Deleting a session does not delete trace files.
- There is no dedicated endpoint yet for reading or editing a study plan.
- A parsed plan can come from a `plan_check` message or a transcript upload.
  Uploads parse immediately; only degrees with `plan_validation_enabled` also
  receive a deterministic validation result.

## Data Flow

```text
POST /api/sessions            # optional body {"degree": "<degree_id>"}
  -> SessionService.create_session(degree_id)
  -> seeds degree_id into the LangGraph checkpoint
  -> returns session_id + degree

POST /api/sessions/{session_id}/message
  -> SessionService.process_message()
  -> LangGraph ainvoke(..., thread_id=session_id)
  -> agent graph updates in-memory ConsultantState

DELETE /api/sessions/{session_id}
  -> SessionService.delete_session()
  -> MemorySaver.delete_thread(session_id)
```

For a normal study question, the graph may store exact course-offering lookup
context and citations, but no study plan.

For a plan-check message, the graph stores:

```text
parsed_study_plan
rule_check_result
```

The API response includes `rule_check_result` when available.

When a later chat message adds or corrects plan information, the parser receives
both the existing `parsed_study_plan` JSON and the latest user message. It must
return one complete updated plan, preserving existing modules while incorporating
the new information. The returned complete plan replaces the previous state and
is enriched and validated again. Initial chat plans and transcript uploads have
no existing-plan input and retain the normal full-plan parsing flow.

## StudyPlan Schema

The canonical in-process schema lives in `backend/app/domain/study_plan.py` and
is shared by all degree programs. Degree-specific semantics live in each degree
package: the parser's JSON schema (`DegreeDefinition.study_plan_schema`)
constrains which fields the LLM fills per degree, and the degree's validator
interprets them. For `msc_informatik` all fields below are used; for
`msc_data_science` the parser only fills `name`, `lp`, and `area`
(`thesis`/`unknown`) — classification happens deterministically against the
canonical module catalogue, and `specialization_area` plus the boolean flags
stay at their defaults.

```python
class StudyPlan(BaseModel):
    specialization_area: Literal["practical", "theoretical", "technical"] | None
    modules: list[PlannedModule]
```

The specialization area is the chosen Vertiefung:

- `practical`
- `theoretical`
- `technical`
- `None` when not supplied or not parseable

## PlannedModule Schema

```python
class PlannedModule(BaseModel):
    name: str
    lp: int
    area: Literal[
        "practical",
        "theoretical",
        "technical",
        "application",
        "thesis",
        "unknown",
    ]
    is_wahlbereich: bool
    is_ungraded: bool
    is_bachelor_module: bool
    counted_in_bachelor: bool | None
    used_for_master_admission: bool | None
    is_scientific_work: bool
    is_software_project: bool
```

Field meaning:

| Field | Meaning |
|---|---|
| `name` | Module name as parsed from the user or normalized from the catalog. |
| `lp` | Leistungspunkte. Missing LP defaults to `0` and becomes a validation error. |
| `area` | Subject area used for LP totals and specialization checks. |
| `is_wahlbereich` | Whether the module is explicitly counted in Wahlbereich. |
| `is_ungraded` | Whether the module is ungraded or non-differentiated. |
| `is_bachelor_module` | Whether the module counts toward the Bachelor-module cap. |
| `counted_in_bachelor` | Whether this credit was already used for the Bachelor degree; `None` when unknown. Independent of module level. |
| `used_for_master_admission` | Whether this credit was used to meet Master admission requirements; `None` when unknown. |
| `is_scientific_work` | Whether it is a Wissenschaftliches Arbeiten module. |
| `is_software_project` | Whether it is a Softwareprojekt module. |

## User Data vs Inferred Data

The study plan parser extracts what the user says. Then the degree's
`enrich_study_plan` fills in deterministic knowledge: `msc_informatik` enriches
through `module_catalog.py` using the shared `domain/data/courses.json` and
`domain/data/degree_modules/msc_informatik.json`; `msc_data_science`
canonicalizes matched names and default LP from its module catalogue in
`domain/degrees/msc_data_science/module_catalog.py`.

User-provided data can include:

- module name
- LP
- area
- specialization area
- whether a module is in Wahlbereich
- whether a module is ungraded
- whether a module is a Bachelor module
- whether its credits were counted in the Bachelor degree or used for Master admission

Catalog-inferred data can include:

- canonical module name
- LP
- area
- ungraded marker
- Bachelor-module marker
- Wissenschaftliches Arbeiten marker
- Softwareprojekt marker

The implementation intentionally keeps the LLM out of final validation. The LLM may parse a plan, but `degree_rules.py` decides whether the plan passes.

## Wahlbereich Handling

`is_wahlbereich` is separate from `area`.

The four credit allocations are 70 LP Informatik, 10 LP Anwendungsbereich,
10 LP Wahlbereich, and 30 LP Masterarbeit. Informatik comprises the 20/10/10 LP
subject minima, 20 additional LP in one specialization subject, and 10 LP freely
distributed within Informatik. Those free Informatik credits are distinct from
the separate 10 LP Wahlbereich.

A module can retain its subject, for example `technical`, while being allocated
only to Wahlbereich. Its LP are excluded from the Informatik/Anwendungsbereich
totals and from subject and specialization minima. The parser requires explicit
allocation; it does not silently move surplus credits into Wahlbereich.

Current behavior:

- Wahlbereich LP is reported as `wahlbereich_lp`.
- Wahlbereich must contain exactly 10 LP.
- Core Softwareprojekt count excludes modules with `is_wahlbereich=true`.
- Total Softwareprojekt count includes them.
- Core Wissenschaftliches Arbeiten count excludes modules with `is_wahlbereich=true`.
- Total Wissenschaftliches Arbeiten count includes them.

The limits apply to the entire plan:

- At least 1 Softwareprojekt belongs in Informatik; no more than 2 count in total.
- At least 2 Wissenschaftliches Arbeiten modules belong in Informatik; no more
  than 4 count in total. At least one Informatik seminar belongs to the specialization.
- Placing a project or seminar in Wahlbereich does not increase these maxima.
- Grading totals cover all 90 LP taught modules, including Wahlbereich, and exclude
  the thesis: 60–65 LP graded and 25–30 LP ungraded.
- The thesis cannot be allocated to Wahlbereich. Its 30 LP are separate; the
  90 LP taught-module requirement is not a thesis-admission prerequisite (the
  SPO requires at least 60 LP of completed Master modules for admission).

## Prior Bachelor Credits

The 15 LP cap covers Bachelor-level modules across Informatik, Anwendungsbereich,
and Wahlbereich. It is independent of when a module was taken. Credits already
used for the Bachelor degree or Master admission cannot count again, even if the
module itself is at Master level. Additional credits outside the Bachelor degree
(normally 180 LP) remain subject to recognition and the cap.

The parser extracts `counted_in_bachelor` and `used_for_master_admission` only from
explicit evidence, otherwise leaving them `None`. Older stored plans default to
unknown. Confirmed reuse produces `bachelor_credit_reuse` or
`admission_credit_reuse`. Missing history on a Bachelor-level module produces
`bachelor_credit_history_unknown`, a warning, so an arithmetic pass is not a
confirmed recognition decision. The plan checker cannot compare with an unseen
Bachelor transcript.

Duplicate modules within the plan remain errors. `project_management_conflict`
also rejects Projektmanagement combined with Grundlagen des Managements von
IT-Projekten or Projektmanagement - Vertiefung, regardless of allocation (§7(9)).

## RuleCheckResult Schema

Validation output is produced by the session degree's validator
(`backend/app/domain/degrees/<degree>/degree_rules.py`); the shared
`RuleIssue`/`RuleCheckResult` models live in `backend/app/domain/rule_check.py`.

```python
class RuleCheckResult(BaseModel):
    is_valid: bool
    summary: str
    totals: dict[str, int]
    issues: list[RuleIssue]
```

The `totals` dict currently includes:

```text
practical_lp
theoretical_lp
technical_lp
application_lp
informatics_lp
module_area_lp
thesis_lp
master_total_lp
ungraded_lp
graded_lp
bachelor_module_lp
wahlbereich_lp
core_scientific_work_count
total_scientific_work_count
core_software_project_count
total_software_project_count
```

Each issue has:

```python
class RuleIssue(BaseModel):
    code: str
    severity: Literal["error", "warning"]
    message: str
    details: dict[str, Any]
```

## Current Limitations

- No persistent student profile exists.
- No explicit `GET /api/sessions/{id}/study-plan` endpoint exists.
- No explicit `PUT /api/sessions/{id}/study-plan` endpoint exists.
- The study plan is extracted from chat text, with follow-up messages applied by
  asking the parser to reproduce the complete updated plan; it is not edited
  through a structured API.
- Because the LLM reproduces the complete plan on a follow-up, an incorrect
  omission or alteration is still possible and should remain visible to the user
  in the Study Plan tab.
- The parser may miss modules when the user writes an ambiguous or incomplete plan.
- Unknown modules can still be included, but they need explicit LP and area data or they produce validation issues/warnings.
- A module slot ("box") on the checklist can accept different suitable courses,
  but course-to-module recognition is not established by LP/area arithmetic or
  a title match. The adviser sees canonical module slots and explains how to
  check a dedicated slot first, justify external equivalence, and keep broad
  slots available for desired future courses. Official recognition belongs to
  the Prüfungsausschuss.
- Proposed alternative placements and reservations for future courses are
  advisory conversation context, not separate persisted slot-reservation state.
  The adviser must not silently change the plan, invent future availability,
  or assume that a broad target module can be counted more than once.
- The adviser must distinguish a planned placement from rebooking a completed
  module. The exam board only permits moving a completed source module to free
  its slot when the source is ungraded; a graded target then receives 4.0.
  `is_ungraded` describes assessment type, not evidence that a module has already
  been completed, and the schema has no actual grade or completion-state field.
- Employment/enrollment intervals, professional-work recognition decisions,
  exam registrations/dates/attempts, grade-improvement eligibility, and approved
  study-abroad agreements are not tracked. Their catalogue sections are advisory;
  an arithmetic pass cannot confirm them. Professional work is not automatically
  added as a recognized Softwareprojekt or as extra degree credits.

## Recommended Phase 2 Persistence

The next clean step is to make the study plan an explicit resource:

```text
GET  /api/sessions/{id}/study-plan
PUT  /api/sessions/{id}/study-plan
POST /api/sessions/{id}/study-plan/check
```

For quick local development, store JSON files:

```text
backend/data/sessions/{session_id}.json
```

Suggested shape:

```json
{
  "session_id": "uuid",
  "created_at": "iso-8601",
  "updated_at": "iso-8601",
  "study_plan": {
    "specialization_area": "practical",
    "modules": []
  },
  "last_rule_check_result": null
}
```

For real deployment, move the same schema to SQLite or Postgres. The API contract should stay the same so the storage backend can change later.
