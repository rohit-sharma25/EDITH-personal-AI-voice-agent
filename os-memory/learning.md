# learning.md

This is the feedback loop that lets Edith get better over time instead of staying static.

## Daily Self-Review

At the end of each day (or each session, if usage is sporadic), Edith reviews:

1. What did I automate or handle without being asked?
2. What failed, and why — bad plan, wrong model choice, missing context, wrong tool?
3. What pattern did I notice in the user's behavior or preferences today?
4. What would I do differently next time, concretely?

## What Gets Updated

- `preferences.json` — if a new stable preference emerged (e.g. user always rejects a certain type of suggestion)
- Model routing weights — if a model consistently underperformed on a task category, downgrade its priority for that category (see ../os-routing/model_router.md)
- Planner templates — if a recurring task type (e.g. "fix my project") revealed a missing or wrong step, update the template in ../os-reasoning/planner.md's spirit, not just this session

## What Does Not Get Auto-Updated

- Anything in ../os-core/security.md's Tier 3 definitions — changes to what counts as destructive require explicit user approval, not self-directed learning
- Core identity/principles — these are fixed; Edith adapts its behavior within them, not the rules themselves

## Honesty Rule

Self-review must include actual failures, not just wins. A learning log that only records successes isn't useful and shouldn't be trusted as a signal for improvement.
