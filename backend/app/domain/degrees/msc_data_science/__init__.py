from app.domain.degrees.definition import DegreeDefinition
from app.domain.degrees.prompt_builder import build_prompts, study_plan_schema
from app.domain.degrees.msc_data_science import prompts
from app.domain.degrees.msc_data_science.degree_rules import validate_study_plan
from app.domain.degrees.msc_data_science.module_catalog import ALL_MODULES, enrich_study_plan
from app.domain.degrees.msc_data_science.program_rules import get_program_rules


PLAN_VALIDATION_ENABLED = False

DEGREE = DegreeDefinition(
    id="msc_data_science",
    display_name="M.Sc. Data Science",
    regulation="2021 Studien- und Pruefungsordnung (FU-Mitteilungen 18/2021)",
    prompts=build_prompts(prompts.SPEC, plan_validation_enabled=PLAN_VALIDATION_ENABLED),
    get_program_rules=get_program_rules,
    validate_study_plan=validate_study_plan,
    study_plan_schema=study_plan_schema(prompts.SPEC),
    enrich_study_plan=enrich_study_plan,
    course_areas=("grundlagen", "life_sciences", "technologies"),
    plan_validation_enabled=PLAN_VALIDATION_ENABLED,
    course_modules={module.id: module.name for module in ALL_MODULES},
)
