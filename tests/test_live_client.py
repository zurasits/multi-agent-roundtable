import unittest
from unittest.mock import patch, MagicMock
from src.backend.live_client import LiveAgentClient

class TestLiveClientFallback(unittest.TestCase):
    
    @patch('src.backend.live_client.os.getenv')
    def test_fallback_to_gemini_when_gpt_key_missing(self, mock_getenv):
        # Mock only GEMINI_API_KEY being present
        def getenv_side_effect(key, default=""):
            if key == "GEMINI_API_KEY": return "dummy_gemini_key"
            return ""
        mock_getenv.side_effect = getenv_side_effect
        
        client = LiveAgentClient()
        
        # Mock the internal generators
        client._generate_gpt = MagicMock(return_value="gpt_response")
        client._generate_claude = MagicMock(return_value="claude_response")
        client._generate_gemini = MagicMock(return_value="gemini_fallback_response")
        
        # Request GPT
        response = client.generate_response("Analyst", ["Hello"], llm_provider="gpt")
        
        # Verify it fell back to Gemini because GPT key was empty
        client._generate_gpt.assert_not_called()
        client._generate_gemini.assert_called_once()
        self.assertEqual(response, "gemini_fallback_response")

    @patch('src.backend.live_client.os.getenv')
    def test_uses_gpt_when_key_present(self, mock_getenv):
        # Mock both GEMINI and GPT keys being present
        def getenv_side_effect(key, default=""):
            if key == "GEMINI_API_KEY": return "dummy_gemini_key"
            if key == "OPENAI_API_KEY": return "dummy_gpt_key"
            return ""
        mock_getenv.side_effect = getenv_side_effect
        
        # We also need to mock openai.OpenAI so it doesn't try to make real connections
        with patch('src.backend.live_client.openai.OpenAI') as MockOpenAI:
            client = LiveAgentClient()
            
            client._generate_gpt = MagicMock(return_value="gpt_response")
            client._generate_gemini = MagicMock(return_value="gemini_fallback_response")
            
            # Request GPT
            response = client.generate_response("Analyst", ["Hello"], llm_provider="gpt")
            
            # Verify it actually used GPT
            client._generate_gpt.assert_called_once()
            client._generate_gemini.assert_not_called()
            self.assertEqual(response, "gpt_response")

if __name__ == '__main__':
    unittest.main()
