# memory.md

Memory is what makes Edith feel like it knows the user rather than resetting every session.

## What Gets Stored

- Active and past projects (goals, repos, deadlines, architecture notes, pending bugs)
- People the user works with or mentions regularly
- Coding style and tooling preferences (languages, frameworks, formatting conventions)
- Writing tone preferences
- Frequently used folders, files, and websites
- Daily/weekly schedule patterns
- Long-term goals, separate from day-to-day tasks
- Recent conversation summaries (not full transcripts — summarized facts)
- Deadlines and recurring commitments
- Debugging habits and recurring failure patterns

## What Does Not Get Stored

- One-off, low-signal details that won't matter again
- Sensitive credentials or secrets (these belong in a secure vault, never in plain memory)
- Anything the user explicitly asks to be forgotten

## Storage Shape (practical, not aspirational)

Start with a plain structured store (e.g. SQLite or a JSON/YAML file per category) — not a vector database. Categories:

- `projects.json` — one entry per project, structured fields
- `preferences.json` — coding style, tone, tools
- `people.json`
- `schedule.json`
- `session_summaries/` — one short summary per session, not raw logs

Only move to embeddings/vector search once plain lookups are actually too slow or too unstructured — don't build that complexity up front.

## Update Rules

- Memory updates happen at the end of the thinking pipeline (see ../os-reasoning/thinking.md, step 8), not mid-task.
- Conflicting information overwrites old information, but Edith should surface the change ("Noted — switching your default branch convention from X to Y") rather than silently overwriting.
- Memory is read before planning, never assumed.