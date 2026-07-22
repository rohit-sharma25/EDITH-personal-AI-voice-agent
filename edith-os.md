# edith-os.md

Master orchestrator. This file contains no intelligence of its own — it defines load order and how the pieces fit together.

## Load Order

1. os-core/identity.md — who Edith is (fixed, never changes at runtime)
2. os-core/principles.md — how Edith behaves (fixed)
3. os-core/security.md — what requires confirmation (fixed, highest priority when in conflict with anything below)
4. os-reasoning/thinking.md — the reasoning pipeline every request goes through
5. os-memory/memory.md — what's remembered and how it's retrieved
6. os-reasoning/planner.md — how a goal becomes an executable plan
7. os-routing/model_router.md — which model handles which sub-task
8. os-routing/execution.md — what tools/systems Edith can actually touch, and at what tier
9. os-capabilities/developer.md — coding-specific capabilities
10. os-capabilities/daily_intelligence.md — the scheduled morning briefing
11. os-memory/learning.md — the self-review/improvement loop

## Precedence

If any two files conflict, resolve in this order: os-core/security.md > os-core/identity.md > os-core/principles.md > everything else. Nothing in os-routing/execution.md, os-capabilities/developer.md, or os-capabilities/daily_intelligence.md may override an os-core/security.md confirmation requirement.

## Phased Build Order (matches the roadmap, not the load order above)

**Phase 1 — Intelligence Foundation**
os-core/identity.md, os-core/principles.md, os-reasoning/thinking.md, os-reasoning/planner.md, os-memory/memory.md

**Phase 2 — AI Operating System**
os-routing/model_router.md, os-routing/execution.md, os-core/security.md, local + browser automation

**Phase 3 — Autonomous Intelligence**
os-capabilities/daily_intelligence.md, os-capabilities/developer.md, os-memory/learning.md, predictive behavior

## Implementation Note

These files define behavior for a model that has real tool-calling access to the described systems. They are not functional on their own — each capability referenced here (open_application, run_shell_command, read_registry, etc.) needs a corresponding real function wired into the agent loop before Edith can act on it. Treat these docs as the spec the code is built against, not a substitute for the code.