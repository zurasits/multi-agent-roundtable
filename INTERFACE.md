# INTERFACE SPECIFICATION

## Purpose
This document is the single source of truth for every technical interface inside the Multi-Agent Roundtable project. All agents build strictly against this contract. No implementation may intentionally diverge from this specification.

---

## Application Flow
The core architecture follows a strict sequential execution loop:
Proposal -> Critique -> Consensus -> Summary

---

## Directories & Target Paths
- Frontend Implementation: src/frontend/app.py (Streamlit)
- Backend Implementation: src/backend/
- Shared Demo Data: demo_data/

---

## Shared Data Models

### RoundtableMessage
Represents an individual turn taken by an agent in the roundtable loop.
Fields:
- id: str (UUID)
- role: str (proposer, critic, consensus)
- sender: str (e.g., "Gemini Proposer")
- timestamp: str (ISO 8601 UTC)
- content: str (The markdown text payload)
- metadata: dict (Contains execution logs, latency metrics, or API tokens)

### RoundtableSession
Represents an active or historic discussion workspace.
Fields:
- session_id: str (UUID)
- topic: str (The main prompt or discussion question)
- participants: list (Array of active agent configurations)
- mode: str (demo, live)
- messages: list (Array of RoundtableMessage objects)
- created_at: str (ISO 8601 UTC)

---

## Application Modes

### Demo Mode (Default)
- Input Source: Reads pre-recorded json transcripts from demo_data/*.json
- Behavior: Replays discussions with a realistic playback delay based on message timestamps to simulate live-agent thinking.
- Network Rule: Absolutely zero network access and no external API calls allowed. Must work flawlessly completely offline.

### Live Mode (Optional)
- Input Source: Executes real-time Gemini LLM API connections.
- Configuration: Managed via environment variables in .env.
- Behavior: Executes live agent discussion loops utilizing the exact same RoundtableSession and RoundtableMessage schema as Demo Mode.

---

## System Events & State Signals
Agents must orchestrate or UI-render the application state reacting to these strict events:
- session_started: Dispatched when a new workspace is initialized.
- proposal_generated: Dispatched when the proposer agent completes its text payload.
- critique_generated: Dispatched when the critic finishes analyzing the proposal.
- consensus_generated: Dispatched when the final agreement block is formed.
- message_rendered: Dispatched when the frontend updates a column layout view.
- session_finished: Dispatched when the database session transitions to persistence.

---

## Component Communication API

### Backend -> Frontend
The backend module exposes the session payload through defined signatures. The frontend consumes:
- Current RoundtableSession state
- Latest RoundtableMessage object
- Playback status flags (idle, processing, rendering, finished)
- Current Application mode (demo, live)

### Frontend -> Backend
The UI application calls backend functional endpoints strictly restricted to:
- start_session(topic: str, mode: str) -> RoundtableSession
- stop_session(session_id: str) -> bool
- load_transcript(path: str) -> RoundtableSession
- get_next_turn(session_id: str, current_index: int) -> RoundtableMessage

---

## Persistence
A local SQLite database manages tracking and portfolio metrics.
Database Schema holds:
- active_sessions (session_id, topic, mode, created_at)
- message_history (id, session_id, role, sender, timestamp, content)

---

## Versioning & Modification Rules
1. Zero Silent Overwrites: Changes to this specification must be processed exclusively by the Interface Agent.
2. Downstream Workflow Pipeline: Any change to INTERFACE.md immediately requires updating the implementations under src/ followed by automated tests under tests/.