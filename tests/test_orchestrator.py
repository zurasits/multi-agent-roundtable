import unittest
import uuid
from src.backend.orchestrator import get_agents, get_messages, submit_message, trigger_roundtable_step

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.session_id_1 = f"test_session_{uuid.uuid4()}"
        self.session_id_2 = f"test_session_{uuid.uuid4()}"

    def test_get_agents(self):
        agents = get_agents()
        self.assertIsInstance(agents, list)
        self.assertTrue(len(agents) > 0)
        self.assertTrue(hasattr(agents[0], 'id'))
        self.assertTrue(hasattr(agents[0], 'name'))
        self.assertTrue(hasattr(agents[0], 'role'))

    def test_submit_and_get_messages(self):
        initial_count = len(get_messages(self.session_id_1))
        self.assertEqual(initial_count, 0)
        
        submit_message(self.session_id_1, "test_agent_1", "Hello from test session 1!")
        
        # Verify message is in session 1 but not in session 2 (session isolation)
        messages_1 = get_messages(self.session_id_1)
        messages_2 = get_messages(self.session_id_2)
        
        self.assertEqual(len(messages_1), 1)
        self.assertEqual(len(messages_2), 0)
        
        self.assertEqual(messages_1[0].agent_id, "test_agent_1")
        self.assertEqual(messages_1[0].content, "Hello from test session 1!")

    def test_trigger_roundtable_step(self):
        submit_message(self.session_id_1, "test_agent_1", "Initial message")
        initial_count = len(get_messages(self.session_id_1))
        
        trigger_roundtable_step(self.session_id_1)
        
        messages = get_messages(self.session_id_1)
        self.assertEqual(len(messages), initial_count + 1)
        
        # Verify session 2 remains empty
        messages_2 = get_messages(self.session_id_2)
        self.assertEqual(len(messages_2), 0)

if __name__ == '__main__':
    unittest.main()
