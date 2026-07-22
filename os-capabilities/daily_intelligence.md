# daily_intelligence.md

Edith runs a scheduled intelligence pass every morning so the user starts the day already briefed.

## Schedule

- 06:30 — collection begins
- 07:00 — report ready

## Collection Sources (configurable — start with 2-3, expand once stable)

- AI news
- Hardware news
- Research papers (arXiv or similar)
- GitHub trending
- Hugging Face releases
- Product Hunt
- Cybersecurity advisories
- Funding news
- Programming / open source updates

## Pipeline

1. Collect from each configured source
2. De-duplicate across sources
3. Analyze and cluster by topic
4. Compare against prior days to surface what's actually new vs. recurring
5. Predict short-term relevance to the user's active projects/interests
6. Generate a short written report (not a wall of links)
7. Store the report in memory (session_summaries or a dedicated daily/ folder)
8. Deliver: dashboard view + optional voice summary

## Report Shape

Keep it short by default — a 5-10 item digest with one line each, not a research paper. Let the user drill into any item for detail on demand, rather than front-loading everything.

## Personal Life Layer (optional, same schedule)

- Weather
- Calendar for the day
- Outstanding tasks / deadlines
- Unread important emails (flagged, not full inbox dump)
- Health reminders (water, movement) — opt-in only, see ../os-memory/memory.md for what's tracked
