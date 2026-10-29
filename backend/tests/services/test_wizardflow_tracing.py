import asyncio
import json
from pathlib import Path

import pytest
import wizardflow
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.domain.degrees import get_degree_or_default
from app.routes import tracing_router
from app.services import wizardflow_service
from app.services.nodes import scope_classifier
from app.services.session_service import SessionService


def messages(client):
    return [r for r in map(json.loads, Path(client.current_path).read_text(encoding="utf-8").splitlines()) if r["type"] == "message"]


@pytest.fixture
def trace(tmp_path, monkeypatch):
    client = wizardflow.init(enabled=True, output_dir=str(tmp_path), nodes=["scope_classifier"], on_error="raise")
    monkeypatch.setattr(wizardflow_service, "tracer", client)
    return client


def test_scope_classifier_logs_exact_input_and_scoped_execution(trace, monkeypatch):
    captured = {}
    class FakeModelService:
        async def invoke(self, prompt, message, format):
            captured.update(prompt=prompt, msg=message)
            return {"content": '{"message_type":"degree_question","include_cross_university_rules":false}'}
    monkeypatch.setattr(scope_classifier, "ModelService", FakeModelService)
    async def execute():
        with wizardflow_service.workflow(enabled=True, title="Question") as run:
            return await scope_classifier.scope_classifier_node({
                "wizardflow_message_id": run.message_id,
                "messages": [{"role": "user", "content": "How many LP do I need?"}],
            })
    result = asyncio.run(execute())
    assert result["message_type"] == "degree_question"
    step = messages(trace)[0]["steps"][0]
    assert step["nodeId"] == "scope_classifier"
    payload = next(p for p in step["payloads"] if p["label"] == "llm_input")
    assert payload["value"] == captured
    assert captured["prompt"] == get_degree_or_default(None).prompts.classifier_system_prompt
    assert captured["msg"] == "Classify the latest user message in this recent conversation:\nuser: How many LP do I need?"


@pytest.mark.parametrize("enabled", [True, False])
def test_concurrent_requests_and_opt_out(trace, monkeypatch, enabled):
    ids = []
    class FakeAgentApp:
        async def ainvoke(self, state, config):
            message_id = state["wizardflow_message_id"]
            ids.append(message_id)
            with wizardflow_service.node_scope(message_id, "scope_classifier") as node:
                await asyncio.sleep(0)
                node.log("input", state["messages"][0]["content"])
            return {"reply": "Answer", "message_type": "degree_question"}
    monkeypatch.setattr("app.services.session_service._get_agent_app", lambda: FakeAgentApp())
    async def execute():
        return await asyncio.gather(*(SessionService().process_message(f"session-{i}", f"Question {i}", tracing_enabled=enabled) for i in range(2)))
    replies = asyncio.run(execute())
    assert all(r.reply == "Answer" for r in replies)
    if enabled:
        assert len(set(ids)) == 2 and all(ids)
        records = messages(trace)
        assert len(records) == 2
        assert {r["steps"][0]["payloads"][0]["value"] for r in records} == {"Question 0", "Question 1"}
    else:
        assert ids == ["", ""]
        assert not Path(trace.current_path).exists()


def test_failure_finalizes_trace_and_preserves_application_error(trace, monkeypatch):
    class FakeAgentApp:
        async def ainvoke(self, state, config):
            with wizardflow_service.node_scope(state["wizardflow_message_id"], "scope_classifier"):
                raise ValueError("test failure")
    monkeypatch.setattr("app.services.session_service._get_agent_app", lambda: FakeAgentApp())
    with pytest.raises(HTTPException) as exc:
        asyncio.run(SessionService().process_message("failed-session", "Question"))
    assert exc.value.status_code == 500
    assert exc.value.detail == "test failure"
    assert len(messages(trace)) == 1
    # Exiting a failed workflow must reset its context for the next request.
    with wizardflow_service.workflow(enabled=True, title="Next") as run:
        with wizardflow_service.node_scope(run.message_id, "scope_classifier") as node:
            node.log("output", "ok")
    assert len(messages(trace)) == 2


def _tracing_client() -> TestClient:
    app = FastAPI()
    app.include_router(tracing_router)
    return TestClient(app)


def test_tracing_reinit_returns_conflict_when_tracing_is_disabled(monkeypatch):
    monkeypatch.setattr(wizardflow_service, "tracer", None)
    monkeypatch.setattr(wizardflow_service.settings.WIZARDFLOW, "ENABLED", False)

    with _tracing_client() as client:
        response = client.post("/api/tracing/reinit")

    assert response.status_code == 409
    assert response.json()["detail"]["error_code"] == "tracing_disabled"


def test_tracing_reinit_starts_a_new_trace_file(tmp_path, monkeypatch):
    tracer = wizardflow.init(enabled=True,
        output_dir=str(tmp_path),
        nodes=["__start__", "scope_classifier", "__end__"],
    )
    old_path = str(tracer.current_path)
    monkeypatch.setattr(wizardflow_service, "tracer", tracer)

    with _tracing_client() as client:
        response = client.post("/api/tracing/reinit")

    assert response.status_code == 200
    new_path = response.json()["trace_path"]
    assert new_path == str(tracer.current_path)
    assert new_path != old_path
