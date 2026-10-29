import asyncio
import json

import pytest

from app.services.nodes import study_plan_parser


def _module(name: str, lp: int, area: str = "unknown") -> dict:
    return {
        "name": name,
        "lp": lp,
        "area": area,
        "is_wahlbereich": False,
        "is_ungraded": False,
        "is_bachelor_module": False,
        "is_scientific_work": False,
        "is_software_project": False,
    }


def test_follow_up_receives_existing_plan_and_returns_complete_update(monkeypatch):
    captured = {}
    existing_module = _module("Existing Module", 10, "technical")
    french_module = _module("French", 5, "application")

    class FakeModelService:
        async def invoke(self, **kwargs):
            captured.update(kwargs)
            return {
                "content": json.dumps(
                    {
                        "specialization_area": None,
                        "modules": [existing_module, french_module],
                    }
                )
            }

    monkeypatch.setattr(study_plan_parser, "ModelService", FakeModelService)

    result = asyncio.run(
        study_plan_parser.study_plan_parser_node(
            {
                "degree_id": "msc_informatik",
                "messages": [{"role": "user", "content": "I forgot about French (5 ECTS)."}],
                "parsed_study_plan": {
                    "specialization_area": None,
                    "modules": [existing_module],
                },
            }
        )
    )

    assert [module["name"] for module in result["parsed_study_plan"]["modules"]] == [
        "Existing Module",
        "French",
    ]
    assert '"name": "Existing Module"' in captured["message"]
    assert "Latest user message:\nI forgot about French (5 ECTS)." in captured["message"]
    assert "Return the complete updated study plan." in captured["message"]


def test_initial_plan_keeps_original_parser_input_shape(monkeypatch):
    captured = {}

    class FakeModelService:
        async def invoke(self, **kwargs):
            captured.update(kwargs)
            return {"content": '{"specialization_area":null,"modules":[]}'}

    monkeypatch.setattr(study_plan_parser, "ModelService", FakeModelService)

    asyncio.run(
        study_plan_parser.study_plan_parser_node(
            {
                "degree_id": "msc_informatik",
                "messages": [{"role": "user", "content": "Here is my study plan."}],
            }
        )
    )

    assert captured["message"] == "User message:\nHere is my study plan."


@pytest.mark.parametrize("bachelor_level", [False, True])
def test_parser_preserves_prior_credit_use_through_enrichment(monkeypatch, bachelor_level):
    module = _module("Rechnersicherheit", 10, "technical")
    module.update(is_bachelor_module=bachelor_level, counted_in_bachelor=True, used_for_master_admission=False)

    class FakeModelService:
        async def invoke(self, **kwargs):
            return {"content": json.dumps({"specialization_area": None, "modules": [module]})}

    monkeypatch.setattr(study_plan_parser, "ModelService", FakeModelService)
    plan = asyncio.run(study_plan_parser.parse_study_plan("This module was counted in my Bachelor degree."))
    assert plan.modules[0].counted_in_bachelor is True
    assert plan.modules[0].used_for_master_admission is False
    assert plan.modules[0].is_bachelor_module is bachelor_level


def test_older_plans_keep_unknown_credit_history():
    from app.domain.study_plan import StudyPlan

    plan = StudyPlan.model_validate({"modules": [_module("Bachelor course", 5)]})
    assert plan.modules[0].counted_in_bachelor is None
    assert plan.modules[0].used_for_master_admission is None
