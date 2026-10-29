# LLM Providers

Configured in `backend/app/settings.py`.

Supported providers:

```text
LLM_PROVIDER=academiccloud   # hosted AcademicCloud API
LLM_PROVIDER=fu_ollama       # FU Ollama on cuda01 via auto SSH tunnel
LLM_PROVIDER=local_ollama    # Ollama running on the host machine
```

Each provider reads its own `<PROVIDER>_*` env vars (model, temperature,
timeout, etc.). The SSH tunnel for `fu_ollama` is started automatically during
app lifespan — there is no separate `USE_SSH` flag. SSH credentials live under
`FU_SSH_USER` / `FU_SSH_PASSWORD` in `.env.local`.

Provider services:

```text
backend/app/services/academiccloud_service.py
backend/app/services/ollama_service.py
backend/app/services/model_service.py
backend/app/services/ssh_manager.py
```

## Model choice

For the AcademicCloud deployment, use
`ACADEMICCLOUD_MODEL=qwen3-30b-a3b-instruct-2507`. It is the deliberate dedicated
instruction-model choice for concise, predictable consultant responses. Do not
switch it to the thinking-capable `qwen3.6-35b-a3b` merely because it may be
stronger overall; its reasoning-oriented behaviour can make user-facing responses
unnecessarily long.

## Operational notes

- `fu_ollama` only works when the computer is connected to the FU Berlin VPN. If
  the SSH tunnel or cuda01 connection fails, check VPN connectivity before
  changing SSH credentials or provider code.
- Use AcademicCloud sparingly. The configured AcademicCloud API key is registered
  for another project too, so avoid unnecessary exploratory calls and prefer
  `local_ollama` or `fu_ollama` for development/testing when practical.

## Prompt convention

Shared prompt text lives in `backend/app/domain/degrees/prompt_builder.py`;
each degree's `prompts.py` only declares a `DegreePromptSpec` (name, regulation,
topics, course types, optional extra rules/examples/parser overrides). Change
shared wording once in the builder, never by copying it into a degree.

- Internal LLM nodes use `domain_scope`.
- Only `AnswerComposer` uses `answer_identity`.
- Keep classifiers, parsers, and course-key selectors terse and task-specific.
- Degree-specific wording stays inside the degree package; nodes must not
  hardcode any degree's terminology.
