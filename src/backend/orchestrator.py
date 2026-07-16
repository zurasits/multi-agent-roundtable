import uuid
import random
from datetime import datetime
from src.backend.db import Agent, Message, get_all_agents, get_session_messages, add_message
from src.backend.live_client import LiveAgentClient

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

def trigger_roundtable_step(session_id: str, live_mode: bool = False) -> None:
    agents = get_all_agents()
    if not agents:
        return
    agent = random.choice(agents)
    
    if live_mode:
        # Construct history
        messages = get_session_messages(session_id)
        # Fast lookup for agent names
        agents_dict = {a.id: a.name for a in agents}
        
        history_strings = []
        # Let's take the last 15 messages so the prompt isn't excessively huge
        for m in messages[-15:]:
            name = "User" if m.agent_id == "live_user" else agents_dict.get(m.agent_id, "Unknown")
            history_strings.append(f"{name}: {m.content}")
            
        client = LiveAgentClient()
        response_text = client.generate_response(agent.role, history_strings)
        submit_message(session_id, agent.id, response_text)
    else:
        # Default mock mode
        submit_message(session_id, agent.id, f"Hello from {agent.name}. I am simulating a step.")
