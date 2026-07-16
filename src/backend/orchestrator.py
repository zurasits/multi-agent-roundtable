import uuid
import random
from datetime import datetime
from src.backend.db import Agent, Message, get_all_agents, get_session_messages, add_message

def get_agents() -> list[Agent]:
    return get_all_agents()

def get_messages(session_id: str) -> list[Message]:
    return get_session_messages(session_id)

def submit_message(session_id: str, agent_id: str, content: str) -> None:
    msg = Message(
        id=str(uuid.uuid4()),
        session_id=session_id,
        agent_id=agent_id,
        content=content,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
    add_message(msg)

def trigger_roundtable_step(session_id: str) -> None:
    agents = get_all_agents()
    if not agents:
        return
    agent = random.choice(agents)
    submit_message(session_id, agent.id, f"Hello from {agent.name}. I am simulating a step.")
