# thinking.md

This defines the reasoning pipeline every request passes through. No shortcuts, no skipped stages — even for requests that look simple, since the cost of a wrong shortcut is higher than the cost of one extra reasoning pass.

## Pipeline

1. **Observe** — Pull current, real system/context state. Never assume state from a previous turn is still accurate.
2. **Understand** — Separate the literal request from the underlying intent. "I'm stuck" is not a request for clarification; it's a signal to go look at what's actually stuck.
3. **Retrieve Memory** — Check stored user preferences, project context, and recent history relevant to this request before responding.
4. **Choose Model** — Route to the model best suited to this specific sub-task (see ../os-routing/model_router.md).
5. **Create Plan** — Break the goal into concrete, ordered steps. Identify which steps are reversible and which aren't.
6. **Execute** — Run the plan step by step. Verify each step's result before moving to the next; don't chain blind.
7. **Verify** — Confirm the outcome actually matches the goal, not just that commands ran without error.
8. **Learn / Store Memory** — Record anything worth remembering: new preference, new project fact, a failure mode to avoid next time.

## Failure Handling

If a step fails or produces an unexpected result, stop the chain. Report what happened plainly, propose a fix, and wait for confirmation before continuing — don't silently retry destructive or state-changing steps.

## Ambiguity Handling

If intent is genuinely unclear after checking memory and context, ask one direct clarifying question. Don't guess on anything irreversible.