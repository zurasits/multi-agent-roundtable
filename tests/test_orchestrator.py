import unittest
from src.backend.orchestrator import get_agents, get_messages, submit_message, trigger_roundtable_step

class TestOrchestrator(unittest.TestCase):
    def test_get_agents(self):
        agents = get_agents()
        self.assertIsInstance(agents, list)
        self.assertTrue(len(agents) > 0)
        self.assertTrue(hasattr(agents[0], 'id'))
        self.assertTrue(hasattr(agents[0], 'name'))
        self.assertTrue(hasattr(agents[0], 'role'))

    def test_submit_and_get_messages(self):
        initial_count = len(get_messages())
        submit_message("test_agent_1", "Hello from test!")
        messages = get_messages()
        self.assertEqual(len(messages), initial_count + 1)
        self.assertEqual(messages[-1].agent_id, "test_agent_1")
        self.assertEqual(messages[-1].content, "Hello from test!")

    def test_trigger_roundtable_step(self):
        initial_count = len(get_messages())
        trigger_roundtable_step()
        messages = get_messages()
        self.assertEqual(len(messages), initial_count + 1)

if __name__ == '__main__':
    unittest.main()
