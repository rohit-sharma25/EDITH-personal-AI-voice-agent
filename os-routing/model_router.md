# model_router.md

Edith does not ask one model everything. It routes each sub-task to whichever model is actually best suited, and the user is never asked to choose.

## Routing Table (starting point — tune based on real results, not assumption)

| Task type | Preferred models |
|---|---|
| Programming / debugging | Claude, DeepSeek, GPT |
| Deep reasoning / architecture | GPT, Claude |
| Long-context / multimodal / search | Gemini |
| Real-time news / current events | Grok, Gemini (web-connected) |
| Documentation / explanation | Claude |
| Offline / privacy-sensitive | Local model (Ollama: Llama, Qwen, Mistral) |

## Routing Logic

1. Classify the sub-task type from the planner's output.
2. Check if the task is privacy-sensitive or requires offline execution — if so, route local regardless of table above.
3. Otherwise route by task type per the table.
4. If a call fails or returns low-confidence output, fall back to the next-best model for that category rather than retrying the same one blindly.
5. Log which model handled which task and how well it performed — this feeds ../os-memory/learning.md.

## Explicit Non-Goal

This is not a voting/ensemble system at launch — one model per sub-task, chosen deliberately, is simpler to debug and reason about than blending multiple outputs. Ensemble routing can be considered later once single-model routing is reliable.
