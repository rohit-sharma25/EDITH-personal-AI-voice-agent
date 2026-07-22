# 📋 E.D.I.T.H. — Master .md File Specification

> **Purpose**: This document defines every `.md` file in the EDITH project — what work it's responsible for, and where it must be located.

---

## 🔷 Project Overview — Two Systems

The EDITH project has **two distinct layers** that share the codebase:

| System | Directory | Purpose | Status |
|--------|-----------|---------|--------|
| **PCE Agent** | `edith/` | The actual running voice assistant (Python + HTML + planning docs) | ✅ **ACTIVE** — fully wired and operational |
| **AI OS Architecture** | Root (`./`) | Planning specs for a broader autonomous AI operating system | 🔧 **ARCHITECTURAL SPECS** — define target behavior for when real tool-calling is wired up. Not yet loaded by the running agent. |

> ⚠️ **Important**: The coordinator (`edith_coordinator.py`) reads from `edith/planning/`, **not** from the AI OS `.md` files. Root-level spec files (now organized under `os-core/`, `os-reasoning/`, `os-memory/`, `os-routing/`, `os-capabilities/`) define the *target architecture* for a fully autonomous AI OS — they are aspirational blueprints, not yet actively loaded by the current running EDITH agent.

---

# 🏗 PART 1: PCE AGENT SYSTEM (`edith/`)

The actual voice-activated assistant that runs on your Windows machine.

## 📁 1A. WORKFLOW PLANNING DOCUMENTS — `edith/planning//`

These define **how EDITH should behave** for each capability. The coordinator reads these to route intents correctly.

| # | File | Purpose / Work | Responsible For |
|---|------|----------------|-----------------|
| 1 | **`identity.md`** | Character personality spec — tone of voice, key phrases, how EDITH addresses the user, acronym explanation | Voice personality, all spoken output |
| 2 | **`voice_wake.md`** | Wake word detection protocol — mic input → keyword match → transcribe → route | Voice engine startup flow |
| 3 | **`ar_interface.md`** | Visual HUD & voice interaction layer spec — what the UI shows and how voice + visuals combine | Frontend UI + voice sync |
| 4 | **`browser_control.md`** | Browser automation protocol — managed Selenium browser, remote debugging port, fallback behavior | All browser open/close/search actions |
| 5 | **`network_access.md`** | Network/browser automation spec — default browser for simple URLs, managed browser for complex DOM tasks | URL opening, web interactions |
| 6 | **`research.md`** | Research pipeline — intelligence sources, AI synthesis model, output format (3 bullets), scheduling | Research queries, scheduled tasks |
| 7 | **`satellite_ops.md`** | Data scraping workflow — target identification → data acquisition via API → AI synthesis | Scraping, data gathering |
| 8 | **`drone_control.md`** | Parallel task execution strategy — thread pools for background research, multiprocessing for browsers | Concurrent task execution |
| 9 | **`error_handling.md`** | Error recovery protocol — identify failure, log to history, notify user with in-character message | All error handling behavior |

### 📍 Location Rule
**All workflow planning docs** go in `edith/planning/`.  
The coordinator (`edith_coordinator.py`) automatically reads from this folder based on command type.

---

## 📁 1B. PCE SYSTEM CONFIG — `edith/`

| # | File | Purpose / Work | Responsible For |
|---|------|----------------|-----------------|
| 10 | **`.pce.md`** | PCE system instructions placeholder — defines the Planning-Coordination-Execution framework | Developer onboarding, system architecture reference |
| 11 | **`history.md`** | **Auto-generated** action & error log — DO NOT EDIT manually. Structured entries with timestamps, component, issue, resolution | All runtime logging (via `logger.py`) |

### 📍 Location Rule
- `.pce.md` stays at `edith/.pce.md` (hidden file, loaded by coordinator)
- `history.md` stays at `edith/history.md` (written by `execution/logger.py`)

---

## 📁 1C. USER-FACING DOCUMENTATION — `edith/docs/` & Root

| # | File | Purpose / Work | Responsible For |
|---|------|----------------|-----------------|
| 12 | **`README.md`** | Project overview for end users — architecture, setup instructions, voice commands, troubleshooting | Onboarding new users |
| 13 | **`quickstart.md`** | PCE system instructions for developers — framework layers, workspace growth, error handling, deployment | Developer reference |

### 📍 Location Rule
- `README.md` goes at **project root** (`./README.md`)
- `quickstart.md` goes at **project root** (`./quickstart.md`)
- HTML documentation pages go in `edith/docs/` or root `docs/`

---

# 🏗 PART 2: AI OS ARCHITECTURE (Root-Level Specs)

These are **planning/specification documents** for a broader autonomous AI operating system that EDITH is evolving into. They define behavior for an AI agent with real tool-calling access.

> **Load order** is defined by `edith-os.md` below — these files are loaded in a specific sequence.

## 📁 2A. CORE IDENTITY & PRINCIPLES (Fixed — Never Change at Runtime)

| # | File | Purpose / Work | Load Order |
|---|------|----------------|------------|
| 14 | **`os-core/identity.md`** | AI OS identity — "You are E.D.I.T.H., an autonomous Personal AI Operating System." Defines purpose, standing rules, tone. **Distinct from** `edith/planning/identity.md` which is the voice character spec. | #1 |
| 15 | **`os-core/principles.md`** | Core governing principles — the 7-Step Loop (Observe→Understand→Think→Plan→Execute→Learn→Improve), non-negotiables, the Override Rule. | #2 |
| 16 | **`os-core/security.md`** | Security & permissions — confirmation gate for destructive actions, observation boundaries, credential handling, audit trail. **Overrides all other files when in conflict.** | #3 |

### 📍 Location Rule
These belong in **`os-core/`** because they define the fixed, foundational identity and behavior rules that everything else builds on.

---

## 📁 2B. REASONING & PLANNING PIPELINES

| # | File | Purpose / Work | Load Order |
|---|------|----------------|------------|
| 17 | **`os-reasoning/thinking.md`** | The reasoning pipeline every request goes through — 8 steps: Observe → Understand → Retrieve Memory → Choose Model → Create Plan → Execute → Verify → Learn/Store Memory. | #4 |
| 18 | **`os-reasoning/planner.md`** | Goal-to-plan conversion — turns a user goal into an ordered, executable sequence of steps with confirmation points. | #6 |

### 📍 Location Rule
These belong in **`os-reasoning/`** because they define the core cognitive architecture used across all tasks.

---

## 📁 2C. MEMORY & LEARNING

| # | File | Purpose / Work | Load Order |
|---|------|----------------|------------|
| 19 | **`os-memory/memory.md`** | Memory system spec — what gets stored (projects, people, preferences, schedules, session summaries), what doesn't, storage shape (JSON/YAML, not vector DB initially), update rules. | #5 |
| 20 | **`os-memory/learning.md`** | Self-improvement feedback loop — daily self-review, what gets updated (preferences, model routing weights, planner templates), what does NOT get auto-updated (security, core identity). | #11 |

### 📍 Location Rule
These belong in **`os-memory/`** because memory and learning are system-wide concerns that apply to every capability.

---

## 📁 2D. MODEL ROUTING & EXECUTION TIERS

| # | File | Purpose / Work | Load Order |
|---|------|----------------|------------|
| 21 | **`os-routing/model_router.md`** | AI model routing table — which model handles which task type (e.g., Claude for programming, Gemini for multimodal, local models for privacy). Fallback logic, non-goals. | #7 |
| 22 | **`os-routing/execution.md`** | Tool control tiers & permissions — what EDITH can actually touch in the system. Three tiers: Read-only (no confirmation), Reversible write (summarize after), Irreversible/high-impact (confirm every time). | #8 |

### 📍 Location Rule
These belong in **`os-routing/`** because they govern how every action is routed and executed across all capabilities.

---

## 📁 2E. CAPABILITY SPECIFICATIONS

| # | File | Purpose / Work | Load Order |
|---|------|----------------|------------|
| 23 | **`os-capabilities/developer.md`** | AI pair programming capabilities — code review, error explanation, documentation generation, architecture suggestions, Git commits, test running. Routes per `os-routing/model_router.md`. | #9 |
| 24 | **`os-capabilities/daily_intelligence.md`** | Scheduled morning briefing — collection sources (AI news, GitHub trending, arXiv, etc.), pipeline (collect→deduplicate→analyze→predict→report), personal life layer (weather, calendar, tasks). | #10 |

### 📍 Location Rule
These belong in **`os-capabilities/`** because they are top-level capability modules that the OS orchestrates.

---

## 📁 2F. MASTER ORCHESTRATOR

| # | File | Purpose / Work | Load Order |
|---|------|----------------|------------|
| 25 | **`edith-os.md`** | **Master orchestrator** — contains no intelligence of its own. Defines the **load order** of all 10 AI OS spec files and the **precedence rules** (os-core/security.md > os-core/identity.md > os-core/principles.md > everything else). Also defines the **phased build roadmap** (Phase 1: Intelligence Foundation, Phase 2: AI OS, Phase 3: Autonomous Intelligence). | Loads all others |

### 📍 Location Rule
Must be at **project root** (`./edith-os.md`) since it orchestrates all other AI OS files.

---

# 🗺 QUICK-REFERENCE MAP

## All 25 `.md` Files at a Glance

```
PROJECT ROOT (./)
├── README.md                         # 📘 User onboarding
├── quickstart.md                     # 📘 PCE developer reference
├── edith-os.md                       # 🧠 Master orchestrator (load order, precedence)
│
├── os-core/
│   ├── identity.md                   # 🧬 AI OS identity (WHO am I)
│   ├── principles.md                 # ⚖️ Governing principles (HOW I behave)
│   └── security.md                   # 🔒 Security & permissions (WHAT needs confirmation)
│
├── os-reasoning/
│   ├── thinking.md                   # 🧠 Reasoning pipeline (HOW I think)
│   └── planner.md                    # 📋 Goal-to-plan conversion (HOW I plan)
│
├── os-memory/
│   ├── memory.md                     # 💾 Memory system (WHAT I remember)
│   └── learning.md                   # 📈 Self-improvement loop (HOW I grow)
│
├── os-routing/
│   ├── model_router.md               # 🔀 Model routing table (WHICH model for what)
│   └── execution.md                  # 🛠️ Tool control tiers (WHAT I can touch)
│
├── os-capabilities/
│   ├── developer.md                  # 💻 Coding capabilities (AI pair programming)
│   └── daily_intelligence.md         # 🌅 Morning briefing pipeline

edith/
├── .pce.md           (HIDDEN FILE)   # 📘 PCE framework definition
├── history.md                        # 📝 Auto-generated action & error log
│
└── planning/                         # ✅ ACTIVE — read by coordinator.py
    ├── identity.md                   # 🎭 Voice character spec (distinct from os-core/identity.md)
    ├── voice_wake.md                 # 🎙️ Wake word detection protocol
    ├── ar_interface.md               # 🖥️ Visual HUD & voice UI spec
    ├── browser_control.md            # 🌐 Browser automation protocol
    ├── network_access.md             # 🌍 Network/browser access spec
    ├── research.md                   # 🔬 Research pipeline spec
    ├── satellite_ops.md              # 📡 Data scraping workflow
    ├── drone_control.md              # 🔄 Parallel task execution
    └── error_handling.md             # ⚠️ Error recovery protocol

───
📁 Other directories containing .html (not .md) files:
    docs/             → User-facing HTML documentation
    edith/docs/       → PCE Agent HTML documentation
    These are for .html files only — any future .md added here should follow the
    "User-Facing Documentation" category in Part 1C.
```

---

# ⚡ IMPORTANT: `identity.md` — Two Different Files!

| File | Location | Purpose |
|------|----------|---------|
| `identity.md` | **`os-core/`** (`./os-core/identity.md`) | **AI OS identity** — "You are E.D.I.T.H., an autonomous Personal AI Operating System." Defines purpose, standing rules, tone for the OS layer. |
| `identity.md` | **edith/planning/** (`edith/planning/identity.md`) | **Voice character spec** — defines the in-character voice personality: boot greeting, key phrases, acronym explanation, tone for TTS output. |

They serve different roles and should NOT be merged.

---

# 🔗 HOW THE FILES WORK TOGETHER

## In the PCE Agent System (`edith/`)

```
Voice Command
    → voice_engine.py reads voice_wake.md for wake detection logic
    → coordinator.py reads planning/ docs based on intent type
    → executor.py calls execution/ scripts
    → logger.py writes to history.md
```

## In the AI OS Architecture (Root)

```
User Request
    → edith-os.md loads files in order:
        1. os-core/identity.md (who am I)
        2. os-core/principles.md (how I behave)
        3. os-core/security.md (what needs confirmation)
        4. os-reasoning/thinking.md (reasoning pipeline)
        5. os-memory/memory.md (check stored context)
        6. os-reasoning/planner.md (create execution plan)
        7. os-routing/model_router.md (choose best AI model)
        8. os-routing/execution.md (execute within permissions)
        9. os-capabilities/developer.md / os-capabilities/daily_intelligence.md (capability modules)
        10. os-memory/learning.md (review and improve)
```

---

*Last updated: July 21, 2026*
