# Skill: Add a Prompt

## When to Use
- Adding a new system prompt for a tool or agent behaviour
- Modifying how the LLM responds (tone, format, grounding rules)
- Creating a prompt for summarisation, comparison, or Q&A

---

## Steps

1. Create the prompt file in `apps/api/prompts/<name>.py`
2. Define as a plain string constant — `UPPER_SNAKE_CASE`
3. Use `{variable}` placeholders for dynamic content
4. Add grounding rules if the prompt uses retrieved context
5. Set temperature appropriately in the service that calls it
6. Test by inspecting raw LLM output before it reaches the user

---

## Conventions

**Location**: `apps/api/prompts/` — one file per concern
**Format**: Plain string constants — not Jinja, not f-strings at definition time
**Naming**: `<PURPOSE>_PROMPT` — e.g. `QA_SYSTEM_PROMPT`, `SUMMARIZE_PROMPT`
**Invocation**: Always through `services/llm.py` — never call OpenAI directly

**Current prompt files**
- `prompts/system.py` — agent system prompt
- `prompts/qa.py` — grounded Q&A prompt
- `prompts/summarize.py` — document summarisation
- `prompts/compare.py` — document comparison

---

## Prompt Structure

Every prompt should have:
1. **Role** — who the LLM is
2. **Task** — what it must do
3. **Constraints** — what it must NOT do
4. **Format** — how to structure the response
5. **Context placeholder** — where retrieved chunks go

---

## Grounding Rules

For any prompt that uses retrieved context:
- State explicitly: "Answer ONLY from the provided context"
- Include the fallback: "If not found, say: I don't have that in my knowledge base"
- Never allow general knowledge to fill gaps

---

## Temperature Guide

| Task | Temperature | Why |
|---|---|---|
| Factual Q&A | 0.0 | Deterministic, grounded |
| Summarisation | 0.0 | Faithful to source |
| Comparison | 0.0 | Structural, factual |
| Creative writing | 0.7 | (Not used in MiniGlean) |

---

## Rules
- No prompt strings in routers or services — always in `prompts/`
- No f-strings at definition — use `.format()` or `{placeholders}` at call time
- Every prompt that receives context must have a grounding constraint
- Temperature is always 0.0 in this project — we want factual answers
- Test prompts by printing raw LLM output — don't trust the final formatted response

---

## Checklist
- [ ] Prompt file in `apps/api/prompts/`
- [ ] Named as `UPPER_SNAKE_CASE` constant
- [ ] Has role, task, constraints, format
- [ ] Grounding rule present if context is provided
- [ ] Uses `{placeholder}` — not hardcoded values
- [ ] Temperature set correctly where the prompt is invoked
- [ ] Tested with real queries — output matches expectations