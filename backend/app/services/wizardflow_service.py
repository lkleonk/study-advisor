import logging
from typing import Any
from contextlib import contextmanager
from types import SimpleNamespace

import wizardflow

from app.settings import settings


logger = logging.getLogger(__name__)

tracer = None


def initialize_wizardflow(agent_app: Any) -> None:
    """Initialize one process-wide WizardFlow tracer from the compiled graph."""
    global tracer

    if not settings.WIZARDFLOW.ENABLED or tracer is not None:
        return

    try:
        tracer = wizardflow.init_from_langgraph(
            agent_app,
            output_dir=str(settings.WIZARDFLOW.OUTPUT_DIR),
            file_prefix=settings.WIZARDFLOW.FILE_PREFIX,
            name="FU Berlin CS Consultant",
            description="LangGraph traces for consultant messages and transcript uploads.",
            meta={
                "llm_provider": settings.provider_name(),
                "llm_model": settings.active_model_name(),
            },
        )
        logger.info("WizardFlow tracing initialized: %s", tracer.current_path)
    except Exception:
        tracer = None
        logger.exception("Failed to initialize WizardFlow tracing")


def reinit_tracing() -> str | None:
    """Start a new trace file, keeping graph and output configuration.

    Returns the new trace path, or None when tracing is disabled. Errors
    propagate so the manual trigger surfaces them instead of silently
    continuing in the old file.
    """
    if tracer is None:
        return None

    path = str(tracer.reinit())
    logger.info("WizardFlow trace file rotated: %s", path)
    return path



_disabled_tracer = wizardflow.Client(enabled=False)


@contextmanager
def workflow(*, enabled: bool, title: str):
    """Own one request trace; opting out never changes the shared tracer."""
    if not enabled or tracer is None:
        yield SimpleNamespace(message_id="")
        return
    with tracer.workflow() as run:
        run.set_info(title=title)
        yield run


def node_scope(message_id: str | None, node_id: str, *, kind: str | None = None):
    """Scope a graph node, including helpers shared with transcript uploads."""
    client = tracer if message_id and tracer is not None else _disabled_tracer
    return client.node(message_id or "disabled", node_id, kind=kind)
