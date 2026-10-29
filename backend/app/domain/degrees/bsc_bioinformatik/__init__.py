"""FU Berlin B.Sc. Bioinformatik, 2023 study and examination regulations.

A joint programme of FU Berlin and the Charité. Provides the rules catalogue,
canonical module list, and course offerings. Deterministic study-plan
validation is not available for this degree.
"""

from app.domain.catalog_data import module_names
from app.domain.degrees.bsc_bioinformatik import prompts
from app.domain.degrees.bsc_bioinformatik.degree_rules import validate_study_plan
from app.domain.degrees.bsc_bioinformatik.program_rules import get_program_rules
from app.domain.degrees.definition import DegreeDefinition
from app.domain.degrees.prompt_builder import build_prompts, study_plan_schema
from app.domain.study_plan import StudyPlan


def enrich_study_plan(plan: StudyPlan) -> StudyPlan:
    """Leave plans unchanged; there is no deterministic Bioinformatik validator yet."""
    return plan


PLAN_VALIDATION_ENABLED = False

DEGREE = DegreeDefinition(
    id="bsc_bioinformatik",
    display_name="B.Sc. Bioinformatik",
    regulation="2023 Studien- und Pruefungsordnung (FU-Mitteilungen 34/2023)",
    prompts=build_prompts(prompts.SPEC, plan_validation_enabled=PLAN_VALIDATION_ENABLED),
    get_program_rules=get_program_rules,
    validate_study_plan=validate_study_plan,
    study_plan_schema=study_plan_schema(prompts.SPEC),
    enrich_study_plan=enrich_study_plan,
    course_areas=("informatik", "mathematik_statistik", "biologie_chemie", "wahlbereich", "abv"),
    plan_validation_enabled=PLAN_VALIDATION_ENABLED,
    course_modules=module_names("bsc_bioinformatik"),
)
