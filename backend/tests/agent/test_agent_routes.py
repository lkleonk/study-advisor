import pytest

from app.domain.degrees import get_degree
from app.services.nodes.scope_classifier import (
    heuristic_classify,
    heuristic_needs_cross_university_rules,
)
from app.services.routing import route_after_classifier


def test_route_after_classifier_plan_check():
    assert route_after_classifier({"message_type": "plan_check"}) == "plan_check"


def test_route_after_classifier_degree_question():
    assert route_after_classifier({"message_type": "degree_question"}) == "degree_question"


def test_route_after_classifier_course_offering_question():
    assert route_after_classifier({"message_type": "course_offering_question"}) == "course_offering_question"


def test_route_after_classifier_defaults_off_topic():
    assert route_after_classifier({"message_type": "unexpected"}) == "off_topic"


def test_heuristic_classifier_detects_degree_question():
    message_type = heuristic_classify("Wie viele LP brauche ich im Anwendungsbereich im Master Informatik?")

    assert message_type == "degree_question"


def test_heuristic_classifier_detects_english_degree_question():
    message_type = heuristic_classify("How many credits do I need for technical CS?")

    assert message_type == "degree_question"


def test_heuristic_classifier_detects_course_offering_question():
    message_type = heuristic_classify("Welche Softwareprojekte gibt es im SoSe 2026?")

    assert message_type == "course_offering_question"


def test_heuristic_classifier_detects_plan_check():
    message_type = heuristic_classify(
        "Bitte prüfe meinen Studienplan: Rechnersicherheit 10 LP, "
        "Softwareprojekt Praktische Informatik B 10 LP, Master Informatik."
    )

    assert message_type == "plan_check"


def test_heuristic_classifier_detects_cross_university_degree_question():
    message = "Can I take and count a course at TU Berlin?"

    assert heuristic_classify(message) == "degree_question"
    assert heuristic_needs_cross_university_rules(message) is True


def test_cross_university_heuristic_stays_off_for_unrelated_rules():
    assert heuristic_needs_cross_university_rules("How many thesis LP do I need?") is False


def test_heuristic_classifier_detects_incremental_plan_information():
    assert heuristic_classify("I forgot about French (5 ECTS).") == "plan_check"


@pytest.mark.parametrize("message", [
    "Wie viele Prüfungsversuche habe ich?",
    "Wie funktioniert die Prüfungsanmeldung?",
    "Kann ich ein abgeschlossenes Modul umbuchen?",
    "Can professional experience replace a Softwareprojekt?",
    "How does grade improvement work?",
    "What should I arrange before study abroad?",
])
def test_administrative_questions_fall_back_to_degree_guidance(message):
    terms = get_degree("msc_informatik").prompts.fallback_domain_terms
    assert heuristic_classify(message, terms) == "degree_question"


@pytest.mark.parametrize("message", [
    "Bitte prüf meinen Studienplan.",
    "Prüfen Sie meinen Studienplan.",
    "Bitte überprüfe: Master Informatik, Rechnersicherheit 10 LP.",
])
def test_german_plan_check_verbs_still_trigger_parsing(message):
    assert heuristic_classify(message) == "plan_check"


def _classify_as_plan_check(monkeypatch, degree_id):
    import asyncio

    from app.services.nodes import scope_classifier

    class FakeModelService:
        async def invoke(self, **kwargs):
            return {"content": '{"message_type": "plan_check", "include_cross_university_rules": false}'}

    monkeypatch.setattr(scope_classifier, "ModelService", FakeModelService)
    state = {"degree_id": degree_id, "messages": [{"role": "user", "content": "Check my plan please"}]}
    return asyncio.run(scope_classifier.scope_classifier_node(state))["message_type"]


def test_plan_check_is_kept_for_degrees_with_plan_validation(monkeypatch):
    assert _classify_as_plan_check(monkeypatch, "msc_informatik") == "plan_check"


def test_plan_check_becomes_degree_question_without_plan_validation(monkeypatch):
    assert _classify_as_plan_check(monkeypatch, "bsc_informatik") == "degree_question"
    assert _classify_as_plan_check(monkeypatch, "msc_data_science") == "degree_question"
