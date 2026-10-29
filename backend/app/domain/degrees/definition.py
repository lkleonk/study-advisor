from dataclasses import dataclass
from typing import Any, Callable

from app.domain.program_rules import ProgramRulesCatalogue
from app.domain.rule_check import RuleCheckResult
from app.domain.study_plan import StudyPlan


@dataclass(frozen=True)
class DegreePrompts:
    domain_scope: str
    answer_identity: str
    classifier_system_prompt: str
    course_key_selector_template: str
    study_plan_parser_system_prompt: str
    answer_composer_system_prompt: str
    offtopic_reply_de: str
    offtopic_reply_en: str
    # Degree-specific keywords for the heuristic classifier fallback, on top of
    # its shared domain terms (normalized: lowercase, umlauts transliterated).
    fallback_domain_terms: tuple[str, ...] = ()


@dataclass(frozen=True)
class DegreeDefinition:
    id: str
    display_name: str
    regulation: str
    prompts: DegreePrompts
    get_program_rules: Callable[[], ProgramRulesCatalogue]
    validate_study_plan: Callable[[StudyPlan | dict[str, Any]], RuleCheckResult]
    # JSON schema constraining the study-plan parser LLM output for this degree.
    study_plan_schema: dict[str, Any]
    # Deterministic post-parse enrichment (canonical names, default LP, flags).
    enrich_study_plan: Callable[[StudyPlan], StudyPlan]
    # Area vocabulary for this degree's course-offering placements.
    course_areas: tuple[str, ...]
    # Canonical module list (id -> display name) when the degree validates as a
    # checklist; placements must then reference these ids. None means the
    # degree has no canonical list and placements carry module_catalog_name.
    course_modules: dict[str, str] | None = None
    # Whether deterministic study-plan validation is trusted for this degree.
    # When False, plan checks are answered as plain degree questions, uploaded
    # transcripts are only extracted into chat context, and the frontend hides
    # the Study Plan tab.
    plan_validation_enabled: bool = False
