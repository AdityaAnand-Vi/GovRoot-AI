# GramSeva AI — The Rural Governance Co-pilot 🌾

> **AI-powered backend for village-level governance.** Built on Gemini 2.5 Flash, GramSeva AI helps Gram Panchayat Secretaries triage infrastructure emergencies, check scheme eligibility, coordinate meetings, and generate weekly intelligence reports — all through a single conversational API.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Agents](#agents)
- [MCP Servers](#mcp-servers)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Running with Docker](#running-with-docker)
- [Testing](#testing)
- [Design Principles](#design-principles)

---

## Overview

GramSeva AI is a multi-agent backend system that acts as a **Rural Governance Co-pilot**. It accepts natural language queries from a Gram Panchayat Secretary (in English or Hinglish) and routes them through a chain of specialised agents to produce structured, actionable recommendations.

**Core capabilities:**

| Capability | Description |
|---|---|
| 🚨 **Infrastructure Triage** | Auto-detects Water, Electricity, Roads, Fire & Medical emergencies; scores and ranks them by priority |
| 📋 **Scheme Intelligence** | Evaluates citizen eligibility for government schemes (e.g. Water Subsidy) using Long Context RAG |
| 🗂️ **Data Integrity** | "Data Desert Protocol" — flags missing citizen records and requests physical verification |
| 📊 **Governance Insights** | Weekly Intelligence Reports identifying hotspots and recommending systemic fixes |
| 📅 **Meeting Coordination** | Auto-detects conflicts and schedules hotspot coordination meetings via Google Calendar MCP |

---

## Architecture

```
User Query (POST /query)
        │
        ▼
┌─────────────────────────────────────────┐
│              Orchestrator               │
│  ┌──────────────┐  ┌─────────────────┐  │
│  │ Step 1: JSON │  │ Step 2: Python  │  │
│  │   Intent     │  │  Tool Router    │  │
│  │  Extraction  │  │  (hard coded    │  │
│  │  (Gemini)    │  │   guard rails)  │  │
│  └──────────────┘  └─────────────────┘  │
│  ┌──────────────────────────────────┐   │
│  │ Step 3: Synthesis (Gemini + SIP) │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
        │
   ┌────┴──────────────────────────────────┐
   │                                       │
   ▼                                       ▼
ComplaintAgent + TaskAgent        SchemeAgent / MeetingAgent
(Water / Fire / Electricity)      (RAG eligibility / Calendar)
        │                                  │
        ▼                                  ▼
  FirestoreClient (Mock DB)       MCP Servers (Calendar / Tasks)
```

**Suggestive Intelligence Pattern (SIP):** Every agent response follows a strict 3-block format:
1. **OBSERVATION** — What the data says
2. **RECOMMENDATION** — Ranked options with logical reasoning
3. **ACTION** — Waits for human `Confirm` before mutating any state (Human-in-the-Loop)

---

## Project Structure

```
GovRoot AI/
├── main.py                    # FastAPI app — /query and /report endpoints
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
├── Dockerfile                 # Container definition
├── .dockerignore
│
├── agents/
│   ├── orchestrator.py        # Multi-stage Intent Router (Gemini 2.5 Flash)
│   ├── complaint_agent.py     # Citizen verification + complaint logging
│   ├── task_agent.py          # Task drafting via Google Tasks MCP
│   ├── scheme_agent.py        # Scheme eligibility RAG (Long Context)
│   ├── meeting_agent.py       # Meeting scheduling + conflict detection
│   └── report_agent.py        # Weekly Intelligence Report generation
│
├── mcp_servers/
│   ├── calendar_server.py     # FastMCP — Google Calendar integration
│   └── tasks_server.py        # FastMCP — Google Tasks integration
│
├── db/
│   └── firestore_client.py    # Firestore helpers (mock DB included)
│
├── policies/
│   ├── water_subsidy_scheme.txt   # Policy document for RAG
│   └── sample_scheme.txt
│
└── test_orchestrator.py       # End-to-end orchestrator tests
```

---

## Agents

### `orchestrator.py` — The Brain
The central router. Runs a **3-step pipeline** for every query:

1. **Intent Extraction** — Calls Gemini to return a clean JSON list of intents (e.g. `["water", "scheme"]`).
2. **Python Tool Router** — Uses `TriageManager` to score intents by weighted priority and dispatches to the correct specialist agent(s). Triage weights:

   | Intent | Weight | Notes |
   |---|---|---|
   | water / medical / fire | 10 | Level 1 — highest priority |
   | electricity | 7 | Level 2 |
   | roads / sanitation | 4 | Level 3 |
   | admin / scheme | 2 | General / Informational |

   Tie-breaker order for simultaneous Level 1s: **Fire (1) > Medical (2) > Water (3)**

3. **Synthesis** — Passes the Python tool output trace back to Gemini for a human-readable, SIP-formatted response. The model cannot hallucinate — it is strictly constrained to the backend trace.

### `complaint_agent.py` — Infrastructure Complaints
Checks citizen registration status in the Firestore DB. If a citizen record is missing, it triggers the **Data Desert Protocol** and requests physical document verification instead of silently failing.

### `task_agent.py` — Task Management
Drafts Google Tasks via MCP, auto-assigning the correct department:
- Water/Pipe issues → **Field Technical Team**
- Road/Pothole → **PWD**
- Electricity → **Electricity Board**
- Everything else → **General Administration**

### `scheme_agent.py` — Scheme Eligibility (RAG)
Reads the `policies/water_subsidy_scheme.txt` policy file and evaluates a citizen's profile (fetched from Firestore) against eligibility criteria using Gemini's long context window. Returns a structured eligibility verdict citing the specific policy clause.

### `meeting_agent.py` — Calendar & Conflict Management
- `check_meeting_conflicts()` — Detects existing calendar blocks and recommends rescheduling during emergencies.
- `manage_meeting()` — Schedules a coordination meeting for "Tomorrow at 10:00 AM" via the Calendar MCP server.

### `report_agent.py` — Weekly Intelligence Reports
Fetches the week's complaints and tasks from Firestore, then uses Gemini to identify **hotspot patterns** (e.g., *"80% of Block 4 complaints are water-related"*) and recommend a long-term systemic fix. Always concludes by suggesting a stakeholder meeting via the Meeting Agent.

---

## MCP Servers

Both servers use **FastMCP** and expose tools compatible with the MCP protocol.

| Server | Tool | Description |
|---|---|---|
| `calendar_server.py` | `schedule_meeting` | Drafts a Google Calendar event with title, time, and attendees |
| `tasks_server.py` | `draft_task` | Creates a task entry in Google Tasks with title, description, and assignee |

---

## API Endpoints

### `POST /query`
The primary endpoint. Routes any natural language input through the orchestrator.

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

---

### `GET /report`
Generates the Weekly Intelligence Report using the Report Agent.

**Response:**
```json
{
  "status": "success",
  "report": "**OBSERVATION**\n...\n**RECOMMENDATION**\n...\n**ACTION**\n..."
}
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- A **Gemini API key** (for local dev) OR a **Google Cloud project** with Vertex AI enabled

### 1. Clone & install dependencies

```bash
git clone <your-repo-url>
cd "GovRoot AI"
pip install -r requirements.txt
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env and fill in your credentials
```

### 3. Run the server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

The API will be available at `http://localhost:8080`.  
Interactive docs: `http://localhost:8080/docs`

---

## Environment Variables

Copy `.env.example` to `.env` and populate the values:

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | For local dev | API key from [Google AI Studio](https://aistudio.google.com/) |
| `GOOGLE_CLOUD_PROJECT` | For Cloud Run / Vertex AI | Your GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | Optional | Vertex AI region (default: `us-central1`) |

> **Note:** The orchestrator prefers `GEMINI_API_KEY` when both are set. In production (Cloud Run), use Workload Identity and set only `GOOGLE_CLOUD_PROJECT`.

---

## Running with Docker

```bash
# Build the image
docker build -t gramseva-ai .

# Run with your API key
docker run -p 8080:8080 \
  -e GEMINI_API_KEY=your_key_here \
  gramseva-ai
```

---

## Testing

```bash
python test_orchestrator.py
```

The test suite exercises the orchestrator's key scenarios:
- **Level 1 Emergency** — Fire + Electricity dual-intent triage
- **Scheme Eligibility** — RAG evaluation for a known citizen (User_A)
- **Data Desert Protocol** — Missing citizen (User_Z) triggers verification flow
- **Graceful Fallback** — Unrecognised intents (e.g. noise complaint) route to General Admin

> Tests include **offline mock responses** so they pass without a live API key.

---

## Design Principles

| Principle | Implementation |
|---|---|
| **Human-in-the-Loop** | No endpoint is called or confirmed without an explicit `Confirm` from the Secretary |
| **Language Mirroring** | English input → English output; Hinglish input → Hinglish output |
| **Suggestive Intelligence** | Every response follows OBSERVATION → RECOMMENDATION → ACTION |
| **Graceful Degradation** | API failures fall back to offline mock blocks; unknown intents fall back to General Admin |
| **Data Integrity First** | Missing citizen records always trigger Data Desert Protocol before any action |
| **Priority-Weighted Triage** | Emergencies are never treated equally — the TriageManager enforces strict ordering |

---

*Built with ❤️ for rural India — powered by Gemini 2.5 Flash.*
