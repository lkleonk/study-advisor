import asyncio

import pytest

from app.services.nodes import answer_composer
from app.services.nodes.answer_composer import AnswerGenerationError


def test_answer_composer_does_not_return_fallback_when_model_fails(monkeypatch):
    class FailingModelService:
        async def invoke(self, **kwargs):
            raise RuntimeError("provider unavailable")

    monkeypatch.setattr(answer_composer, "ModelService", FailingModelService)

    state = {
        "degree_id": "msc_informatik",
        "messages": [{"role": "user", "content": "How many LP are required?"}],
        "wizardflow_message_id": "test-message",
    }

    with pytest.raises(AnswerGenerationError):
        asyncio.run(answer_composer.answer_composer_node(state))


@pytest.mark.parametrize(
    ("include_cross_university_rules", "expect_cross_university_context"),
    [(False, False), (True, True)],
)
def test_answer_composer_conditionally_includes_cross_university_rules(
    monkeypatch,
    include_cross_university_rules,
    expect_cross_university_context,
):
    captured = {}

    class CapturingModelService:
        async def invoke(self, **kwargs):
            captured.update(kwargs)
            return {"content": '{"message":"Answer"}'}

    monkeypatch.setattr(answer_composer, "ModelService", CapturingModelService)

    state = {
        "degree_id": "msc_informatik",
        "messages": [{"role": "user", "content": "What are the rules?"}],
        "wizardflow_message_id": "test-message",
        "include_cross_university_rules": include_cross_university_rules,
    }

    asyncio.run(answer_composer.answer_composer_node(state))

    has_cross_university_context = "COURSES AT HU BERLIN AND TU BERLIN" in captured["message"]
    assert has_cross_university_context is expect_cross_university_context
    assert "SOFTWAREPROJEKT" in captured["message"]
