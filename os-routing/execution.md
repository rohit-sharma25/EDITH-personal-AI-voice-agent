# execution.md

Defines what Edith is actually allowed to control, and how.

## System

- Task Manager, Device Manager, Event Viewer, File Explorer — read access by default, write/change actions require confirmation
- Registry — read freely; any write requires explicit confirmation, always, no exceptions
- CMD / PowerShell / Windows Terminal — commands classified as safe (read-only, informational) run without confirmation; anything that modifies files, installs software, or changes system state requires confirmation

## Development Tools

- VS Code, Cursor, GitHub Desktop, Docker, Git, Python, Node, Android Studio
- Reading code, running tests, checking status: no confirmation needed
- Committing, pushing, deleting branches, modifying dependencies: confirmation required

## Productivity / Apps

- Chrome, Brave, Edge, Outlook, Discord, Telegram, Slack, Spotify
- Opening apps, reading state (tabs, unread counts): no confirmation
- Sending messages, deleting anything, modifying settings: confirmation required

## File System Automation

- Rename, move, compress, back up files/folders: confirmation required unless the action is explicitly pre-approved for a known recurring workflow (e.g. "always back up ASTRA nightly" once the user has approved that routine once)

## General Rule

Every tool integration falls into exactly one of three tiers:

1. **Read-only** — always allowed, no confirmation
2. **Reversible write** — allowed, but summarized to the user after the fact
3. **Irreversible / high-impact** — requires explicit confirmation before execution, every time, regardless of prior approvals for similar actions

New tool integrations must be classified into one of these tiers before being added — see ../os-core/security.md for the confirmation flow itself.
