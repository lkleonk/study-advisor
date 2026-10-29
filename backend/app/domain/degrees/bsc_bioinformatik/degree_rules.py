"""Placeholder study-plan response for B.Sc. Bioinformatik.

Plan validation is disabled for this degree (plan_validation_enabled=False), so
this validator is not used at runtime; it only satisfies the DegreeDefinition
contract until deterministic B.Sc. Bioinformatik rules are implemented.
"""

from typing import Any

from app.domain.rule_check import RuleCheckResult, RuleIssue
from app.domain.study_plan import StudyPlan


def validate_study_plan(raw_plan: StudyPlan | dict[str, Any]) -> RuleCheckResult:
    plan = StudyPlan.model_validate(raw_plan)
    return RuleCheckResult(
        is_valid=False,
        summary=(
            "B.Sc. Bioinformatik plan checking is not available yet. The Degree Rules tab lists the "
            "current requirements."
        ),
        totals={"listed_module_lp": sum(module.lp for module in plan.modules)},
        issues=[
            RuleIssue(
                code="bsc_bioinformatik_plan_validation_unavailable",
                severity="warning",
                message="No deterministic B.Sc. Bioinformatik plan validation is available yet.",
            )
        ],
    )
