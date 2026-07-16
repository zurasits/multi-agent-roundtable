import os
from google import genai

class LiveAgentClient:
    """Client for calling Google Gemini API using credentials from environment variables."""
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def generate_response(self, agent_role: str, conversation_history: list) -> str:
        """Calls Gemini API to generate the next response in the roundtable."""
        if not self.client:
            return f"[Live Client] Kann nicht mit Gemini verbinden. (Kein GEMINI_API_KEY in .env gefunden für Rolle: {agent_role})"
        
        # Build prompt
        prompt = f"Du spielst folgende Rolle in einer Multi-Agenten-Diskussion:\n{agent_role}\n\n"
        prompt += "Hier ist der bisherige Gesprächsverlauf:\n"
        for msg in conversation_history:
            prompt += f"{msg}\n"
        
        prompt += "\nBitte antworte jetzt passend zu deiner Rolle auf den Gesprächsverlauf. Bleibe kurz und prägnant."

        try:
            response = self.client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
            )
            return response.text
        except Exception as e:
            # Fallback for high demand / rate limits
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.1-flash-lite',
                    contents=prompt,
                )
                return response.text
            except Exception as e2:
                err_str = str(e2)
                # Parse out the clean error message to hide JSON from user
                if "'message': '" in err_str:
                    start = err_str.find("'message': '") + 12
                    end = err_str.find("'", start)
                    if end > start:
                        clean_msg = err_str[start:end]
                        return f"[System-Hinweis] {clean_msg}"
                
                # Default friendly error if parsing fails
                return "[System-Hinweis] Das KI-Modell ist temporär überlastet. Bitte versuchen Sie es in wenigen Sekunden erneut."
