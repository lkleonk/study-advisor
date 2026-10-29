"""FU Berlin M.Sc. Physik, 2024 study and examination regulations.

Provides the rules catalogue, canonical module list, and course offerings.
Deterministic study-plan validation is not available for this degree.
"""

from app.domain.catalog_data import module_names
from app.domain.degrees.definition import DegreeDefinition
from app.domain.degrees.msc_physik import prompts
from app.domain.degrees.msc_physik.degree_rules import validate_study_plan
from app.domain.degrees.msc_physik.program_rules import get_program_rules
from app.domain.degrees.prompt_builder import build_prompts, study_plan_schema
from app.domain.study_plan import StudyPlan


def enrich_study_plan(plan: StudyPlan) -> StudyPlan:
    """Leave plans unchanged; there is no deterministic Physik validator yet."""
    return plan


PLAN_VALIDATION_ENABLED = False

DEGREE = DegreeDefinition(
    id="msc_physik",
    display_name="M.Sc. Physik",
    regulation="2024 Studien- und Pruefungsordnung (FU-Mitteilungen 12/2024)",
    prompts=build_prompts(prompts.SPEC, plan_validation_enabled=PLAN_VALIDATION_ENABLED),
    get_program_rules=get_program_rules,
    validate_study_plan=validate_study_plan,
    study_plan_schema=study_plan_schema(prompts.SPEC),
    enrich_study_plan=enrich_study_plan,
    course_areas=("compulsory", "compulsory_elective", "elective", "research_phase"),
    plan_validation_enabled=PLAN_VALIDATION_ENABLED,
    course_modules=module_names("msc_physik"),
)
