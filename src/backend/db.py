from dataclasses import dataclass
from typing import List

@dataclass
class Agent:
    id: str
    name: str
    role: str

@dataclass
class Message:
    id: str
    agent_id: str
    content: str
    timestamp: str

agents_db = [
    Agent(id="agent_1", name="Alice", role="Analyst"),
    Agent(id="agent_2", name="Bob", role="Reviewer")
]

messages_db: List[Message] = []
