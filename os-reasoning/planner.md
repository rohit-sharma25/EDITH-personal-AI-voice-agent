# planner.md

The planner turns a goal into an ordered, executable sequence of steps. The user should rarely have to spell out each step themselves.

## Planning Structure

Goal → Context Gathering → Sub-tasks → Tool/Model Assignment → Execution Order → Confirmation Points → Execute → Explain Result

## Example: "Fix my project"

1. Identify the active project from memory/context
2. Inspect project state (open terminal, check recent errors/logs)
3. Read and categorize the errors
4. Search documentation / prior known fixes for this error type
5. Compare candidate solutions
6. Generate a proposed fix
7. Explain the fix and the reasoning in plain terms
8. Wait for user confirmation if the fix touches files, dependencies, or config
9. Apply the fix
10. Verify (re-run tests / re-check the failure condition)

## Rules for the Planner

- Every plan should have explicit confirmation points before any irreversible step — not just one blanket confirmation at the start.
- Plans should be shown to the user in short form before execution when the task is non-trivial (more than 2–3 steps, or touches files/system state).
- If a step in the plan fails, the planner re-plans from that point — it does not blindly continue the original sequence.
- Trivial, fully reversible tasks (e.g. "open VS Code") skip the full planning ceremony and just execute.