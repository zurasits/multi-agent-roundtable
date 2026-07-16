import json
import os
from datetime import datetime
from src.backend.db import Message, add_message

def load_demo_transcript(session_id: str, file_path: str) -> None:
    """Reads a JSON transcript file and loads its messages into the database under session_id."""
    if not os.path.exists(file_path):
        return
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return
        
        for index, item in enumerate(data):
            base_id = item.get("id", f"demo_{index}")
            msg = Message(
                id=f"{base_id}_{session_id}",
                session_id=session_id,
                agent_id=item.get("agent_id", "agent_1"),
                content=item.get("content", ""),
                timestamp=item.get("timestamp", datetime.utcnow().isoformat() + "Z")
            )
            add_message(msg)
