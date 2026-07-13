import uuid
from datetime import datetime
from src.backend.db import Agent, Message, agents_db, messages_db

def get_agents() -> list[Agent]:
    return agents_db

def get_messages() -> list[Message]:
    return messages_db

def submit_message(agent_id: str, content: str) -> None:
    msg = Message(
        id=str(uuid.uuid4()),
        agent_id=agent_id,
        content=content,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
    messages_db.append(msg)

def trigger_roundtable_step() -> None:
    if not agents_db:
        return
    import random
    agent = random.choice(agents_db)
    submit_message(agent.id, f"Hello from {agent.name}. I am simulating a step.")
