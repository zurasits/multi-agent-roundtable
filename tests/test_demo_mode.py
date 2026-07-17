import unittest
import uuid
import os
import socket
from src.backend.db import get_session_messages
from src.backend.demo_loader import load_demo_transcript

class BlockedNetworkTestCase(unittest.TestCase):
    """Base test case that actively blocks network connections to guarantee offline execution."""
    def setUp(self):
        self._original_socket = socket.socket
        # Replace socket.socket with a dummy function that throws an error on connect
        def blocked_socket(*args, **kwargs):
            raise socket.error("Network connection blocked by design in Tester Agent test suite.")
        socket.socket = blocked_socket

    def tearDown(self):
        socket.socket = self._original_socket

class TestDemoModeOffline(BlockedNetworkTestCase):
    def test_demo_mode_offline_loading(self):
        session_id = f"test_demo_{uuid.uuid4()}"
        demo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../demo_data/transcript_001.json")
        
        # Load transcript offline - should succeed since it's zero-network dependency
        load_demo_transcript(session_id, demo_path)
        
        messages = get_session_messages(session_id)
        self.assertTrue(len(messages) > 0)
        self.assertEqual(messages[0].agent_id, "agent_1")
        self.assertIn("Multi-Agent Collaborative System", messages[0].content)

if __name__ == '__main__':
    unittest.main()
