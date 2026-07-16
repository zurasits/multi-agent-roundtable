import os

class LiveAgentClient:
    """Stub client for calling live LLM APIs using credentials from environment variables."""
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY", "")

    def generate_response(self, agent_role: str, conversation_history: list) -> str:
        """Simulates calling a live LLM API if key is present; otherwise returns a mock response."""
        if not self.api_key:
            return f"[Live Client] Simulating response for {agent_role} (No LLM_API_KEY found in .env)"
        return f"[Live Client] Real LLM API response for role '{agent_role}'"
