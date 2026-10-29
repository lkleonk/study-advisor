from app.domain.degrees.definition import DegreeDefinition
from app.domain.degrees.prompt_builder import build_prompts, study_plan_schema
from app.domain.degrees.msc_informatik import prompts
from app.domain.degrees.msc_informatik.degree_rules import validate_study_plan
from app.domain.degrees.msc_informatik.program_rules import get_program_rules
from app.domain.module_catalog import course_modules, enrich_study_plan


PLAN_VALIDATION_ENABLED = True

DEGREE = DegreeDefinition(
    id="msc_informatik",
    display_name="M.Sc. Informatik",
    regulation="2014 Studien- und Pruefungsordnung",
    prompts=build_prompts(prompts.SPEC, plan_validation_enabled=PLAN_VALIDATION_ENABLED),
    get_program_rules=get_program_rules,
    validate_study_plan=validate_study_plan,
    study_plan_schema=study_plan_schema(prompts.SPEC),
    enrich_study_plan=enrich_study_plan,
    course_areas=("technical", "practical", "theoretical", "application"),
    course_modules=course_modules(),
    plan_validation_enabled=PLAN_VALIDATION_ENABLED,
)
