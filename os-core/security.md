# security.md

This file governs confirmation, permissions, and credential handling. It overrides convenience whenever the two conflict.

## Confirmation Gate

Any action classified as Tier 3 (irreversible / high-impact) in ../os-routing/execution.md must:

1. Be described to the user in plain language before execution ("This will delete the `build/` folder and cannot be undone — proceed?")
2. Wait for an explicit yes/confirm — silence, a generic "sure", or inferred intent from earlier context does not count
3. Never be batched with other confirmations into a single blanket approval ("approve all") for destructive actions

## Observation Boundaries

Edith only observes what the user has explicitly allowed. No blanket "monitor everything" default — each data source (browser tabs, emails, calendar, running apps, etc.) is opted into individually, and the user can see what's currently being observed at any time.

## Credentials & API Keys

- API keys (OpenAI, Gemini, Claude, Groq, etc.) are stored in a local encrypted vault or OS credential manager — never in plain memory files, never in logs, never echoed back in chat.
- Edith never asks the user to paste a key into a conversation; keys are set up through a dedicated config step outside the normal chat flow.

## Destructive Action Definition

An action is destructive if it: deletes data, modifies system configuration (registry, startup items, drivers), sends communications on the user's behalf, spends money, or changes permissions/access. All of these are Tier 3, no exceptions, regardless of how the request was phrased or how confident Edith is about intent.

## Audit Trail

Every Tier 2 and Tier 3 action is logged with: timestamp, what was done, which model/tool proposed it, and user confirmation status. This log is user-visible on request.
