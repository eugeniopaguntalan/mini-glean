# Skill: Debug Agent Behaviour

## When to Use
- Agent picks the wrong tool
- Agent loops without producing an answer
- Agent ignores conversation history
- Agent hallucinates a tool that doesn't exist
- Agent calls a tool with malformed arguments

---

## How the Agent Decides

1. Read system prompt → understand role and constraints
2. Read chat history → understand conversation context
3. Read all tool docstrings → understand available capabilities
4. Decide: call a tool OR respond directly
5. If tool called → read tool output → generate final answer

The agent's decision quality depends on: **system prompt clarity** + **tool docstring specificity** + **memory state**.

---

## Diagnosis Steps

### 1. Wrong tool selected
- Check the tool docstrings — are they ambiguous?
- Does the correct tool clearly state WHEN to use it?
- Does it state when NOT to use it?
- Fix: make docstrings more specific and mutually exclusive

### 2. Agent loops (max iterations hit)
- Check `max_iterations` in `services/agent.py` (currently 5)
- Check if the tool is returning an error the agent keeps retrying
- Check if the tool output is confusing the agent into calling itself again
- Fix: return a definitive string from the tool — "done" or "not found"

### 3. Agent ignores chat history
- Check `ConversationBufferWindowMemory(k=6)` — is k too low?
- Check `memory_key` matches the prompt's `MessagesPlaceholder` key
- Is the session ID being reused correctly across requests?
- Fix: verify session management in the `/chat` endpoint

### 4. Agent hallucinates a tool
- The agent is inventing tool names not in the registry
- Check if `handle_parsing_errors=True` is set in `AgentExecutor`
- Fix: strengthen system prompt with "You can ONLY use the tools listed below"

### 5. Malformed tool arguments
- Agent passes wrong types or missing required fields
- Check the tool's `args_schema` — are `Field(description=...)` clear?
- Fix: make descriptions more explicit about expected format

---

## Key Agent Configuration

| Setting | Value | Location |
|---|---|---|
| Model | `gpt-4o` | `services/agent.py` |
| Temperature | 0.0 | `services/agent.py` |
| Memory window | 6 messages | `services/agent.py` |
| Max iterations | 5 | `services/agent.py` |
| Handle parsing errors | True | `services/agent.py` |
| Verbose | True (dev) / False (prod) | `services/agent.py` |

---

## Quick Fixes

| Symptom | Most Likely Cause | Fix |
|---|---|---|
| Always picks `search` | Other tool docstrings too vague | Make docstrings more specific |
| Calls `compare` with one ID | Docstring doesn't say "requires two" | Add constraint to docstring |
| Infinite loop | Tool returns ambiguous output | Return definitive "done" or "not found" |
| Forgets earlier messages | Session ID not persisted | Check session management in `/chat` route |
| Invents a tool | System prompt too permissive | Add "ONLY use listed tools" constraint |
| Answers from general knowledge | Grounding prompt too weak | Strengthen "ONLY from context" rule |

---

## Debugging Workflow

1. Set `verbose=True` in `AgentExecutor` — see full reasoning chain
2. Check which tool the agent chose and why
3. Check the tool input — were arguments correct?
4. Check the tool output — was it useful to the agent?
5. Check the final answer — did it cite sources?

---

## Rules
- Always check docstrings first — 80% of agent bugs are docstring clarity issues
- Don't increase `max_iterations` past 5 — if it takes more, something is wrong
- Don't add memory beyond 6 messages — it dilutes relevance
- When in doubt, set `verbose=True` and read the agent's full reasoning trace