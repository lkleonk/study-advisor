"""FU Berlin B.Sc. Informatik, 2023 study and examination regulations.

This initial degree package intentionally provides the authoritative rules
catalogue only. Canonical module mappings, course offerings, and deterministic
study-plan validation will be added once their source data is available.
"""

from app.domain.degrees.definition import DegreeDefinition
from app.domain.degrees.prompt_builder import build_prompts, study_plan_schema
from app.domain.degrees.bsc_informatik import prompts
from app.domain.degrees.bsc_informatik.degree_rules import validate_study_plan
from app.domain.degrees.bsc_informatik.program_rules import get_program_rules
from app.domain.catalog_data import module_names
from app.domain.study_plan import StudyPlan


def enrich_study_plan(plan: StudyPlan) -> StudyPlan:
    """Leave B.Sc. plans unchanged until a canonical module catalogue exists."""
    return plan


PLAN_VALIDATION_ENABLED = False

DEGREE = DegreeDefinition(
    id="bsc_informatik",
    display_name="B.Sc. Informatik",
    regulation="2023 Studien- und Pruefungsordnung (FU-Mitteilungen 23/2023)",
    prompts=build_prompts(prompts.SPEC, plan_validation_enabled=PLAN_VALIDATION_ENABLED),
    get_program_rules=get_program_rules,
    validate_study_plan=validate_study_plan,
    study_plan_schema=study_plan_schema(prompts.SPEC),
    enrich_study_plan=enrich_study_plan,
    course_areas=("compulsory", "compulsory_elective", "free_elective", "abv"),
    plan_validation_enabled=PLAN_VALIDATION_ENABLED,
    course_modules=module_names("bsc_informatik"),
)
