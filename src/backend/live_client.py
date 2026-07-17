import os
from datetime import datetime
from google import genai
from dotenv import load_dotenv

class LiveAgentClient:
    """Client for calling Google Gemini API using credentials from environment variables."""
    def __init__(self):
        load_dotenv() # Ensure .env is loaded if running locally without docker
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def generate_response(self, agent_role: str, conversation_history: list) -> str:
        """Calls Gemini API to generate the next response in the roundtable."""
        if not self.client:
            return f"[Live Client] Cannot connect to Gemini. (No GEMINI_API_KEY found in .env for role: {agent_role})"
        
        # Build prompt
        current_date = datetime.now().strftime("%Y-%m-%d")
        prompt = f"You are playing the following role in a multi-agent discussion:\n{agent_role}\n"
        prompt += f"For info: Today's date is {current_date}.\n\n"
        prompt += "Here is the conversation history so far:\n"
        for msg in conversation_history:
            prompt += f"{msg}\n"
        
        prompt += "\nPlease respond to the conversation history in character. Keep it brief and concise."

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
                        return f"[System] {clean_msg}"
                
                # Default friendly error if parsing fails
                return "[System] The AI model is temporarily overloaded. Please try again in a few seconds."
