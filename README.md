# GovRoot AI — The Rural Governance Co-pilot 🌾

> **AI-powered multi-agent system for rural governance.** GovRoot AI helps Gram Panchayat Secretaries triage infrastructure emergencies, check scheme eligibility, coordinate meetings, and generate weekly intelligence reports — through a natural, conversational interface powered by Google ADK and Gemini on Vertex AI.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Agents](#agents)
- [MCP Servers](#mcp-servers)
- [Running Modes](#running-modes)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Running with Docker](#running-with-docker)
- [Testing](#testing)
- [Design Principles](#design-principles)

---

## Overview

GovRoot AI is a **multi-agent backend system** built on [Google ADK](https://google.github.io/adk-docs/) and **Gemini 2.5 Flash Lite** via **Vertex AI**. It accepts natural language queries from a Gram Panchayat Secretary — in English, Hindi, or Hinglish — and routes them through a chain of specialist agents to produce structured, actionable responses.

**Core capabilities:**

| Capability | Description |
|---|---|
| 🚨 **Infrastructure Triage** | Auto-detects Water, Electricity, Roads, Fire & Medical emergencies; ranks them by weighted priority |
| 📋 **Scheme Intelligence** | Evaluates citizen eligibility for government schemes using Long Context RAG on policy documents |
| 🗂️ **Data Integrity** | "Data Desert Protocol" — flags missing citizen records and requests physical verification |
| 📊 **Governance Insights** | Weekly Intelligence Reports identifying hotspots and recommending systemic fixes |
| 📅 **Meeting Coordination** | Detects scheduling conflicts and books hotspot coordination meetings via Google Calendar MCP |

---

## Architecture

GovRoot AI has **two interfaces** that share the same backend agent pipeline:

```
┌────────────────────────────────────────────────────────────┐
│                    ADK Web Interface                       │
│     (Primary — conversational chat via `adk web`)          │
│          govroot_ai/agent.py (root_agent)                  │
└────────────────────┬───────────────────────────────────────┘
                     │ calls query_tool / report_tool
                     │
┌────────────────────▼───────────────────────────────────────┐
│                 FastAPI REST API (Secondary)                │
│          POST /query   ·   GET /report   ·   GET /          │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────────────────────┐
│                     Orchestrator                          │
│                                                           │
│  Step 1 ─ Intent Extraction (Vertex AI / Gemini)          │
│           → returns JSON list of intents                  │
│                                                           │
│  Step 2 ─ Python Tool Router (TriageManager)              │
│           → hardcoded guard-rails, priority weighted      │
│           → dispatches to specialist agents               │
│                                                           │
│  Step 3 ─ Synthesis (Vertex AI / Gemini)                  │
│           → ADK agent reformats conversationally          │
└───────┬───────────────────────────────────┬───────────────┘
        │                                   │
        ▼                                   ▼
ComplaintAgent + TaskAgent       SchemeAgent / MeetingAgent
(Water / Fire / Electricity)     (RAG eligibility / Calendar)
        │                                   │
        ▼                                   ▼
  Firestore Client (Mock DB)    MCP Servers (Calendar / Tasks)
```

### Language Mirroring
The ADK agent detects the language of **every message independently**:
- English input → 100% English response
- Hinglish input → 100% Hinglish response
- Hindi (Devanagari) → Hindi response

### Suggestive Intelligence Pattern (SIP)
The orchestrator backend always returns structured output:
**OBSERVATION** → **RECOMMENDATION** (ranked options) → **ACTION** (waits for human `Confirm`)

The ADK conversational layer then rewrites this naturally, removing rigid headers for a warm, colleague-like tone.

---

## Project Structure

```
GovRoot AI/
├── agent.py                       # Root ADK agent entry point (simple / legacy)
├── main.py                        # FastAPI app — REST API interface
├── requirements.txt
├── .env.example                   # Environment variable template
├── Dockerfile                     # Runs `adk web` (ADK interface)
├── .gitignore
│
├── govroot_ai/                    # PRIMARY ADK agent package
│   ├── __init__.py
│   └── agent.py                   # root_agent with full conversational persona
│
├── agents/
│   ├── orchestrator.py            # 3-step Intent → Router → Synthesis pipeline
│   ├── complaint_agent.py         # Citizen verification + complaint logging
│   ├── task_agent.py              # Task drafting via Google Tasks MCP
│   ├── scheme_agent.py            # Scheme eligibility RAG (Long Context)
│   ├── meeting_agent.py           # Meeting scheduling + conflict detection
│   └── report_agent.py            # Weekly Intelligence Report generation
│
├── mcp_servers/
│   ├── calendar_server.py         # FastMCP — Google Calendar integration
│   └── tasks_server.py            # FastMCP — Google Tasks integration
│
├── db/
│   └── firestore_client.py        # Firestore helpers (mock DB for dev)
│
├── policies/
│   ├── water_subsidy_scheme.txt   # Policy document used for RAG
│   └── sample_scheme.txt
│
└── test_orchestrator.py           # End-to-end orchestrator tests
```

---

## Agents

### `govroot_ai/agent.py` — ADK Conversational Layer
The **primary interface**. A Google ADK `Agent` wrapping `process_query` and `generate_weekly_report` as tools. Handles:
- Per-message language detection (English / Hinglish / Hindi)
- Warm, empathetic conversational reformatting of backend output
- Identity / greeting handling
- Model: `gemini-2.5-flash-lite`

### `agents/orchestrator.py` — The Backend Brain
Runs a **3-step pipeline** for every query:

1. **Intent Extraction** — Calls Vertex AI Gemini to return a clean JSON list of intents (e.g. `["water", "meeting"]`).
2. **Python Tool Router** — `TriageManager` scores intents by weighted priority and dispatches to specialist agents. For Level 1 emergencies, `check_meeting_conflicts` is also automatically called.

   | Intent | Weight | Notes |
   |---|---|---|
   | water / medical / fire | 10 | Level 1 — highest priority |
   | electricity | 7 | Level 2 |
   | roads / sanitation | 4 | Level 3 |
   | admin / scheme | 2 | General / Informational |

   Tie-breaker for simultaneous Level 1s: **Fire (1) > Medical (2) > Water (3)**

3. **Synthesis** — Backend trace passed back to Gemini to generate natural, fact-grounded output for the ADK layer to reformat.

### `agents/complaint_agent.py` — Infrastructure Complaints
Verifies citizen registration in the database. Missing records trigger the **Data Desert Protocol** — requesting physical document verification instead of silently failing.

### `agents/task_agent.py` — Task Management
Drafts Google Tasks via MCP, auto-assigning departments:

| Issue | Assigned To |
|---|---|
| Water / Pipe | Field Technical Team |
| Road / Pothole | PWD |
| Electricity | Electricity Board |
| Other | General Administration |

### `agents/scheme_agent.py` — Scheme Eligibility (RAG)
Reads `policies/water_subsidy_scheme.txt` and evaluates a citizen's Firestore profile against eligibility criteria using Gemini's long context window. Returns a verdict citing the specific policy clause. Now uses **Vertex AI** (`vertexai.generative_models.GenerativeModel`).

### `agents/meeting_agent.py` — Calendar & Conflict Management
- `check_meeting_conflicts()` — detects existing calendar blocks; recommends rescheduling during Level 1 emergencies.
- `manage_meeting()` — schedules a coordination meeting via the Calendar MCP server; supports custom requested time extracted from user text.

### `agents/report_agent.py` — Weekly Intelligence Reports
Fetches the week's complaints and tasks from Firestore, then uses Gemini to identify **hotspot patterns** and recommend a long-term systemic fix. Concludes by suggesting a stakeholder meeting.

---

## MCP Servers

Both servers use **FastMCP** and expose tools compatible with the MCP protocol.

| Server | Tool | Description |
|---|---|---|
| `calendar_server.py` | `schedule_meeting` | Drafts a Google Calendar event with title, time (10:00 AM slot), and attendees |
| `tasks_server.py` | `draft_task` | Creates a Google Tasks entry with title, description, and assignee |

---

## Running Modes

GovRoot AI supports two run modes that share the same backend.

### Mode 1: ADK Web (Primary — Conversational Chat)

```bash
adk web
```

Opens a chat UI at `http://localhost:8000`. Select `govroot_ai` from the agent dropdown. This is the **recommended way** to interact with GovRoot AI — it provides the full conversational, language-aware experience.

### Mode 2: FastAPI REST API (Secondary — Programmatic Access)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

API available at `http://localhost:8080`. Interactive docs at `http://localhost:8080/docs`.

---

## API Endpoints

### `GET /`
Health check.
```json
{"service": "GovRoot AI", "status": "running", "docs": "/docs"}
```

### `POST /query`
Routes any natural language input through the orchestrator.

**Request:**
```json
{
  "text": "Check User_A's eligibility for the water subsidy scheme."
}
```
**Response:**
```json
{
  "status": "success",
  "response": "**OBSERVATION**\n...\n**RECOMMENDATION**\n...\n**ACTION**\n..."
}
```

### `GET /report`
Generates the Weekly Intelligence Report.
```json
{
  "status": "success",
  "report": "**OBSERVATION**\n...\n**RECOMMENDATION**\n...\n**ACTION**\n..."
}
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- A **Google Cloud project** with Vertex AI API enabled
- `gcloud` CLI authenticated (`gcloud auth application-default login`)

### 1. Clone & install dependencies

```bash
git clone https://github.com/AdityaAnand-Vi/GovRoot-AI.git
cd GovRoot-AI
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your Google Cloud project details
```

### 3. Run (ADK Web — recommended)

```bash
adk web
```

Visit `http://localhost:8000` and select **govroot_ai**.

### 4. Run (FastAPI REST — optional)

```bash
uvicorn main:app --reload --port 8080
```

---

## Environment Variables

Copy `.env.example` to `.env` and populate:

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_CLOUD_PROJECT` | ✅ Yes | Your GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | Optional | Vertex AI region (default: `us-central1`) |
| `GEMINI_API_KEY` | Local dev only | API key from [Google AI Studio](https://aistudio.google.com/) — not used in production |

> **Production note:** On Cloud Run, use **Workload Identity Federation** instead of API keys. Set only `GOOGLE_CLOUD_PROJECT` and let the service account handle authentication.

---

## Running with Docker

The Docker image runs the **ADK web interface** by default.

```bash
# Build
docker build -t govroot-ai .

# Run
docker run -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT=your_project_id \
  govroot-ai
```

Access the ADK chat UI at `http://localhost:8080`.

---

## Testing

```bash
python test_orchestrator.py
```

Covers the orchestrator's key scenarios:

| Scenario | What's tested |
|---|---|
| Level 1 Emergency | Fire + Electricity dual-intent triage with tie-breaker |
| Scheme Eligibility | RAG evaluation for a known citizen (User_A) |
| Data Desert Protocol | Missing citizen (User_Z) triggers verification flow |
| Graceful Fallback | Unrecognised intents (e.g. noise complaint) route to General Admin |

> Tests include **offline mock responses** — they pass without a live Vertex AI connection.

---

## Design Principles

| Principle | Implementation |
|---|---|
| **Human-in-the-Loop** | No state is mutated without an explicit `Confirm` from the Secretary |
| **Language Mirroring** | Per-message language detection — English, Hinglish, or Hindi |
| **Conversational First** | ADK layer rewrites backend output naturally, dropping rigid SIP headers |
| **Vertex AI Native** | All Gemini calls go through `vertexai.generative_models` — production-ready |
| **Graceful Degradation** | API failures return structured error messages; unknown intents fall to General Admin |
| **Data Integrity First** | Missing citizen records always trigger Data Desert Protocol before any action |
| **Priority-Weighted Triage** | `TriageManager` enforces strict priority ordering with tie-breaker resolution |

---

*Built for rural India — powered by Gemini 2.5 Flash Lite on Vertex AI and Google ADK.* 🌾
