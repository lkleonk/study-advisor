import asyncio
import json

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
