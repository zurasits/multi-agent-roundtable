# INTERFACE.md - Multi-Agent Roundtable System

## 1. System Components
- **Backend Orchestrator** (`src/backend/`): Manages the state of the multi-agent roundtable discussion, agent registration, and message routing.
- **Frontend App** (`src/frontend/app.py`): Streamlit user interface to display the roundtable conversation in real-time.

## 2. Data Models

### Agent
```python
from dataclasses import dataclass

@dataclass
class Agent:
    id: str
    name: str
    role: str
```

### Message
```python
from dataclasses import dataclass

@dataclass
class Message:
    id: str
    session_id: str
    agent_id: str
    content: str
    timestamp: str
```

## 3. Backend Contracts

The backend exposes the following internal Python API functions that the frontend consumes:

### `get_agents() -> list[Agent]`
Returns the list of all registered agents in the system.

### `get_messages(session_id: str) -> list[Message]`
Returns the current discussion transcript for the specified `session_id`.

### `submit_message(session_id: str, agent_id: str, content: str) -> None`
Allows the frontend to submit a message on behalf of a live user or an external source for a specific `session_id`.

### `trigger_roundtable_step(session_id: str) -> None`
Instructs the backend to execute one turn of the multi-agent discussion for the specified `session_id`, invoking the respective agents.

## 4. Database Schema (SQLite)
The persistent database must contain the following tables:
*   `agents`: Contains `id` (TEXT PRIMARY KEY), `name` (TEXT), and `role` (TEXT).
*   `messages`: Contains `id` (TEXT PRIMARY KEY), `session_id` (TEXT), `agent_id` (TEXT), `content` (TEXT), and `timestamp` (TEXT).

## 5. Demo Data Contract
The `demo_data/transcript_001.json` file must contain a JSON array of `Message` objects with appropriate values.