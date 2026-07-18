import os
from datetime import datetime
from google import genai
import openai
import anthropic
from dotenv import load_dotenv

class LiveAgentClient:
    """Client for calling LLM APIs using credentials from environment variables."""
    def __init__(self):
        load_dotenv() # Ensure .env is loaded if running locally without docker
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        
        self.gemini_client = None
        if self.gemini_key:
            self.gemini_client = genai.Client(api_key=self.gemini_key)
            
        self.openai_client = None
        if self.openai_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_key)
            
        self.anthropic_client = None
        if self.anthropic_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)

    def generate_response(self, agent_role: str, conversation_history: list, llm_provider: str = "gemini") -> str:
        """Calls the respective LLM API to generate the next response."""
        
        # Build system prompt
        current_date = datetime.now().strftime("%Y-%m-%d")
        system_prompt = f"You are playing the following role in a multi-agent discussion:\n{agent_role}\n"
        system_prompt += f"For info: Today's date is {current_date}.\n\nPlease respond to the conversation history in character. Keep it brief and concise."
        
        provider = llm_provider.lower()
        
        if provider == "gpt" and self.openai_client:
            return self._generate_gpt(system_prompt, conversation_history)
        elif provider == "claude" and self.anthropic_client:
            return self._generate_claude(system_prompt, conversation_history)
        else:
            # Fallback to Gemini if requested, or if GPT/Claude API keys are missing
            return self._generate_gemini(system_prompt, conversation_history)

    def _generate_gpt(self, system_prompt: str, history: list) -> str:
        if not self.openai_client:
            return "[System] Cannot connect to GPT. No OPENAI_API_KEY found in .env."
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": "user", "content": msg})
            
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[System Error - GPT] {str(e)}"

    def _generate_claude(self, system_prompt: str, history: list) -> str:
        if not self.anthropic_client:
            return "[System] Cannot connect to Claude. No ANTHROPIC_API_KEY found in .env."
            
        # Claude expects purely string content for user messages in simple setup
        prompt = ""
        for msg in history:
            prompt += f"{msg}\n"
            
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            return f"[System Error - Claude] {str(e)}"

    def _generate_gemini(self, system_prompt: str, history: list) -> str:
        if not self.gemini_client:
            return "[System] Cannot connect to Gemini. No GEMINI_API_KEY found in .env."
            
        prompt = f"{system_prompt}\n\nHere is the conversation history so far:\n"
        for msg in history:
            prompt += f"{msg}\n"
            
        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
            )
            return response.text
        except Exception as e:
            try:
                response = self.gemini_client.models.generate_content(
                    model='gemini-3.1-flash-lite',
                    contents=prompt,
                )
                return response.text
            except Exception as e2:
                err_str = str(e2)
                if "'message': '" in err_str:
                    start = err_str.find("'message': '") + 12
                    end = err_str.find("'", start)
                    if end > start:
                        clean_msg = err_str[start:end]
                        return f"[System] {clean_msg}"
                return "[System] The AI model is temporarily overloaded. Please try again in a few seconds."

    def transcribe_audio(self, audio_bytes: bytes) -> str:
        """Transcribes audio bytes to text using Google Gemini."""
        if not self.gemini_client:
            return "[System] Cannot transcribe audio. No GEMINI_API_KEY found in .env."
            
        try:
            from google.genai import types
            prompt = (
                "You are a professional transcriptionist. Transcribe the ENTIRE attached audio clip word for word. "
                "Do NOT summarize. Do NOT stop early. Do NOT add any extra commentary or text. "
                "Output ONLY the exact spoken words in the original language."
            )
            contents_payload = [
                types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                prompt
            ]
            
            try:
                response = self.gemini_client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=contents_payload
                )
                return response.text.strip()
            except Exception as primary_e:
                # Fallback to a lighter model if rate limit or quota is exhausted
                response = self.gemini_client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=contents_payload
                )
                return response.text.strip()
                
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                return "[System] ⚠️ API-Limit erreicht. Google blockiert gerade weitere Anfragen, weil zu viele auf einmal gesendet wurden. Bitte warte etwa 1 Minute."
            
            # Try to extract a clean message if it's a JSON string
            if "'message': '" in err_str:
                start = err_str.find("'message': '") + 12
                end = err_str.find("'", start)
                if end > start:
                    clean_msg = err_str[start:end]
                    return f"[System] {clean_msg}"
                    
            return f"[System Error - Gemini Audio] {err_str}"

