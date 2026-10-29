# Agent Flow

This document describes the LangGraph flow used by the FU Berlin CS consultant.

The graph is defined in:

```text
backend/app/services/agent_graph_service.py
```

The shared graph state is defined in:

```text
backend/app/services/states/consultant_state.py
```

Agent-flow tuning defaults are defined in:

```text
backend/app/services/agent_config.py
```

## High-Level Flow

```text
START
  -> ScopeClassifier
      -> off_topic                -> OfftopicReply -> END
      -> degree_question          -> AnswerComposer -> END
      -> course_offering_question -> CourseKeySelector -> CourseLookup -> AnswerComposer -> END
      -> plan_check               -> StudyPlanParser -> RuleChecker -> AnswerComposer -> END
```

Every session is bound to one degree program. `SessionService.create_session`
seeds `degree_id` into the LangGraph checkpoint, and every node resolves the
session's `DegreeDefinition` via `degree_for(state)`
(`backend/app/services/nodes/utils.py`), falling back to `DEFAULT_DEGREE_ID`
(`msc_informatik`). Prompts, parse schemas, enrichment, and validators all come
from the degree registry (`backend/app/domain/degrees/`); the LLM never chooses
the degree.

Degree rules are rendered from the session degree's `program_rules.py` and
supplied to `AnswerComposer` as reference context, not embedded in classifier or
composer system prompts. The large `cross-university-courses` section is omitted
unless `ScopeClassifier` marks the current question as needing it. The
`plan_check` path skips course lookup entirely. It only exists for degrees with
`DegreeDefinition.plan_validation_enabled` (currently `msc_informatik`): for
every other degree `ScopeClassifier` downgrades `plan_check` to
`degree_question`, so no rule verdict is produced, and `AnswerComposer` is told
that automatic plan validation is unavailable. Pure degree-rule questions on the
`degree_question` path also skip course lookup and go straight to
`AnswerComposer`. Course-offering questions on the `course_offering_question`
path use exact lookup buckets from the session degree's projection of
`backend/app/domain/data/course_offerings/<semester>.json`.

## State Keys

| State key | Producer | Consumer |
|---|---|---|
| `messages` | API input, `answer_composer`, `offtopic` | all LLM nodes |
| `degree_id` | `SessionService.create_session` (checkpoint seed) | every node via `degree_for(state)` |
| `wizardflow_message_id` | `SessionService` | every active node, WizardFlow finalization |
| `message_type` | `scope_classifier` | graph router, downstream nodes |
| `include_cross_university_rules` | `scope_classifier` | `answer_composer` rule-context renderer |
| `course_lookup_keys` | `course_key_selector` | `course_lookup`, `answer_composer` |
| `course_lookup_invalid_keys` | `course_key_selector` | `course_lookup` |
| `course_lookup_needs_clarification` | `course_key_selector` | `course_lookup`, `answer_composer` |
| `course_lookup_clarification_question` | `course_key_selector` | `course_lookup`, `answer_composer` |
| `course_lookup_message` | `course_key_selector` | `course_lookup`, `answer_composer` |
| `course_context` | `course_lookup` | `answer_composer` |
| `citations` | `course_lookup` | API response |
| `parsed_study_plan` | `study_plan_parser` | `rule_checker` |
| `rule_check_result` | `rule_checker` | `answer_composer`, API response |
| `reply` | `answer_composer`, `offtopic` | API response |

`messages` uses an append reducer, so new user and assistant messages are appended to the session thread.

## Node Responsibilities

### ScopeClassifier

File:

```text
backend/app/services/nodes/scope_classifier.py
```

Purpose:

- Classify the latest user message.
- Return one of:
  - `degree_question`
  - `course_offering_question`
  - `plan_check`
  - `off_topic`

Behavior:

- Uses the active LLM provider.
- Receives a configurable two-user-turn conversation window by default
  (`AGENT_SCOPE_CLASSIFIER_HISTORY_TURNS`) so contextual follow-ups can be
  classified correctly.
- Returns `include_cross_university_rules=true` only for HU/TU
  cross-registration questions and contextual follow-ups about that topic.
- Does not receive the full degree-rule catalogue.
- Falls back to a local heuristic if the LLM call fails.
- Does not answer the user.

### CourseKeySelector

File:

```text
backend/app/services/nodes/course_key_selector.py
```

Purpose:

- Select exact course-offering bucket keys from the local tree.
- Output keys in `semester/area/course_type` format, for example
  `sose26/technical/swp`.
- Output multiple keys for broad questions, for example all SWP buckets in a
  semester when no area is specified.
- Ask for clarification when the user asks about course offerings but omits the
  semester.

Behavior:

- Short-circuits without an LLM call when the session's degree has no tagged
  course-offering entries (`has_offerings(degree_id)` is false), returning an
  honest "no local course-offering data" note for the composer.
- Uses the active LLM provider with the session degree's selector template and
  that degree's projected lookup tree.
- Falls back to a local heuristic if the LLM call fails.
- Does not output course-specific slugs or title filters; title matching is left
  to the final answer over the returned buckets.
- Receives a configurable recent conversation window
  (`AGENT_COURSE_SELECTOR_HISTORY_TURNS`, default `2`).
- The prompt includes a semester coverage note derived from the degree's
  projection of the semester offering files, for example that only `sose26` is
  currently present.

### CourseLookup

File:

```text
backend/app/services/nodes/course_lookup.py
```

Purpose:

- Validate selector keys against the session degree's projected bucket tree
  from the canonical course catalogue and semester offering files.
- Return the whole selected buckets as deterministic `course_context`.
- Add bucket-level citations. Course URL lines and URL-based citations are
  included only when `AGENT_COURSE_LOOKUP_INCLUDE_COURSE_URLS=true`; the default
  is `false`, so individual course URLs are not exposed to `AnswerComposer`.

Output:

```text
course_context
citations
```

Course lookup runs only on the `course_offering_question` path. Pure degree
questions go directly from `ScopeClassifier` to `AnswerComposer`. Plan checks
rely on the deterministic Python validator plus the rendered degree-rule
reference context, so they do not use course lookup.

### StudyPlanParser

File:

```text
backend/app/services/nodes/study_plan_parser.py
```

Purpose:

- Extract a structured `StudyPlan` from the user's message.

Behavior:

- Uses the active LLM provider with the session degree's structured JSON schema
  (`DegreeDefinition.study_plan_schema`).
- For a chat follow-up, receives the existing parsed plan JSON plus the latest
  message and returns a complete updated plan. Initial plans and transcript
  parsing do not include an existing plan.
- Falls back to a heuristic parser if the LLM call fails.
- Enriches parsed modules through the degree's `enrich_study_plan` (the Master
  uses `module_catalog.py`; Data Science canonicalizes names/LP from its
  catalogue).

Important:

- The parser is not trusted for final validity.
- It only creates structured input for the deterministic rule checker.

### RuleChecker

File:

```text
backend/app/services/nodes/rule_checker.py
```

Purpose:

- Run deterministic validation on `parsed_study_plan`.

Implementation (selected via the session degree's `validate_study_plan`):

```text
backend/app/domain/degrees/msc_informatik/degree_rules.py
backend/app/domain/degrees/msc_data_science/degree_rules.py
```

Output:

```text
rule_check_result
```

This node owns the actual pass/fail decision. For the Master Informatik that
covers LP totals, specialization requirements, seminar/project counts,
Wahlbereich caveats, ungraded LP, Bachelor-module LP, and duplicate modules.
For Data Science it covers Grundlagen completeness, profile inference and
mandatory modules, elective quotas, thesis LP/admission, and duplicates.

### AnswerComposer

File:

```text
backend/app/services/nodes/answer_composer.py
```

Purpose:

- Produce the final assistant response.

Inputs:

- Latest user message
- Configurable recent conversation window
  (`AGENT_ANSWER_COMPOSER_HISTORY_TURNS`, default `4`)
- Degree-rule reference context rendered from the selected degree's structured
  catalogue. It normally contains every section except
  `cross-university-courses`; that section is added when the classifier flag is
  true.
- Course-offering context from exact local lookup, when applicable
- Optional deterministic rule-check result

Rules:

- Answer in the same language as the user.
- Use only supplied degree rules, course-offering context, and deterministic
  validation results.
- Do not invent Studienordnung or Pruefungsordnung rules.
- State uncertainty when the local resources do not answer the question.
- Keep the answer advisory.

### Offtopic

File:

```text
backend/app/services/nodes/offtopic.py
```

Purpose:

- Return a short redirect for messages unrelated to the session's degree
  program (reply text comes from the degree's prompts).

Behavior:

- Uses a simple German/English heuristic.
- Does not call the LLM.

## Routing Logic

`route_after_classifier()` lives in:

```text
backend/app/services/routing.py
```

It maps:

```text
plan_check               -> study_plan_parser
degree_question          -> answer_composer
course_offering_question -> course_key_selector (then course_lookup, then answer_composer)
everything else          -> offtopic
```

## WizardFlow Tracing

WizardFlow 0.9.0 uses `with trace.workflow() as run` to finalize each request,
including failures, and node context managers to capture execution timing.
Chat graph nodes and transcript parsing/validation share the same scoped API.
Per-request tracing opt-out uses no-op scopes and writes no trace data.

`SessionService` creates an SDK-generated workflow ID for each chat request or transcript upload
and stores it in `ConsultantState.wizardflow_message_id`. The same workflow ID is passed
to each node and finalized once at the request boundary.

The compiled graph topology is registered through
`wizardflow.init_from_langgraph`. All active nodes log explicitly:

- LLM nodes: `llm_input`, `llm_output`, `llm_error`, and `node_output`.
- Deterministic nodes: `node_input` and `node_output`.

Only executed application nodes are recorded; synthetic `__start__` and
`__end__` graph markers are omitted.

Each `llm_input` contains both the exact system `prompt` and provider `msg`.
Transcript parser messages are intentionally unredacted. Generated JSONL files
are written to `backend/traces/` by default and excluded from Git.

## Error Handling Strategy

LLM-dependent nodes use local fallbacks where possible:

- `ScopeClassifier`: heuristic classifier
- `CourseKeySelector`: heuristic selector
- `StudyPlanParser`: heuristic module/LP parser
- `AnswerComposer`: compact fallback answer

Course lookup failures return an empty context, empty citations, or a concise
clarification/missing-data note.

This keeps the API responsive even when the LLM fails.

## HTML Overview

A visual graph is available in:

```text
docs/agent-flow.html
```
