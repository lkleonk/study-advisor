"""FU Berlin M.Sc. Computational Sciences, 2025 study and examination regulations.

Includes the 2026 amendment (EUMaster4HPC double master). Provides the rules
catalogue, canonical module list, and course offerings. Deterministic
study-plan validation is not available for this degree.
"""

from app.domain.catalog_data import module_names
from app.domain.degrees.definition import DegreeDefinition
from app.domain.degrees.msc_computational_sciences import prompts
from app.domain.degrees.msc_computational_sciences.degree_rules import validate_study_plan
from app.domain.degrees.msc_computational_sciences.program_rules import get_program_rules
from app.domain.degrees.prompt_builder import build_prompts, study_plan_schema
from app.domain.study_plan import StudyPlan


def enrich_study_plan(plan: StudyPlan) -> StudyPlan:
    """Leave plans unchanged; there is no deterministic Computational Sciences validator yet."""
    return plan


PLAN_VALIDATION_ENABLED = False

DEGREE = DegreeDefinition(
    id="msc_computational_sciences",
    display_name="M.Sc. Computational Sciences",
    regulation="2025 Studien- und Pruefungsordnung (FU-Mitteilungen 21/2025), amended 2026 (27/2026)",
    prompts=build_prompts(prompts.SPEC, plan_validation_enabled=PLAN_VALIDATION_ENABLED),
    get_program_rules=get_program_rules,
    validate_study_plan=validate_study_plan,
    study_plan_schema=study_plan_schema(prompts.SPEC),
    enrich_study_plan=enrich_study_plan,
    course_areas=(
        "synchronisation",
        "scientific_computing_a",
        "scientific_computing_b",
        "molecular_sciences",
        "geosciences",
        "atmospheric_sciences",
        "specialisation_shared",
    ),
    plan_validation_enabled=PLAN_VALIDATION_ENABLED,
    course_modules=module_names("msc_computational_sciences"),
)
