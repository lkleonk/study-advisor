import asyncio
import json

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
    # Slot planning applies even when the detailed HU/TU section is excluded.
    assert "CHECKLIST AND KEEP OPTIONS OPEN" in captured["message"]
    assert "Telematik (10 LP)" in captured["message"]
    assert "future course may need it" in captured["message"]
    assert "Prefer a suitable dedicated named" in captured["prompt"]
    assert "approval is not automatic" in captured["message"]
    for title in (
        "REBOOKING COMPLETED MODULES", "PROFESSIONAL EXPERIENCE AS A SOFTWAREPROJEKT",
        "COURSE AND EXAM REGISTRATION", "EXAM ATTEMPTS AND GRADE IMPROVEMENT",
        "PLAN STUDY ABROAD BEFORE DEPARTURE",
    ):
        assert title in captured["message"]
    assert "only when A is ungraded" in captured["message"]
    assert "outside university enrollment" in captured["message"]
    assert "ask about recorded grading if unknown" in captured["prompt"]


@pytest.mark.parametrize("degree_id", ["msc_informatik", "bsc_informatik"])
def test_composer_preserves_markdown_lists_emphasis_and_source_links(monkeypatch, degree_id):
    from app.domain.degrees import get_degree

    source = get_degree(degree_id).get_program_rules().sections[0].sources[0].path
    reply = (
        "Diese Optionen sind im Regelkontext genannt:\n\n"
        "- **Modul A** — 5 LP\n"
        "- **Modul B** — 10 LP\n\n"
        f"Beachte die [Studienordnung]({source})."
    )

    class FormattedModelService:
        async def invoke(self, **kwargs):
            return {"content": json.dumps({"message": reply}, ensure_ascii=False)}

    monkeypatch.setattr(answer_composer, "ModelService", FormattedModelService)
    result = asyncio.run(answer_composer.answer_composer_node({
        "degree_id": degree_id,
        "message_type": "degree_question",
        "messages": [{"role": "user", "content": "Welche unbenoteten Module gibt es?"}],
    }))

    assert result["reply"] == reply
    assert result["messages"] == [{"role": "assistant", "content": reply}]
