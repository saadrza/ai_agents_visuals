# test.py
import os
import sys
import unittest
from dotenv import load_dotenv


# Try importing the agent builder
# We wrap this to provide a clear error if the module is missing
try:
    from agent.orchestrator import build_agent
except ImportError:
    build_agent = None
    print("Warning: Could not import 'agent.orchestrator'. Agent tests will be skipped.")

# --- Helper for Output Parsing (Logic from main.py) ---
def _mock_extract_output(response):
    """Replicating main.py logic for testing purposes."""
    if isinstance(response, dict) and "messages" in response:
        final = response["messages"][-1]
        return getattr(final, 'content', str(final))
    if isinstance(response, dict):
        return response.get("output", str(response))
    return str(response)


class TestDataAnalysisAgent(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Runs once before all tests."""
        load_dotenv()
        cls.api_key = os.getenv("OPENAI_API_KEY")
        # Define the database path you want to test
        cls.test_db_path = "input_files/database/northwind_small.sqlite"

    def test_01_environment_setup(self):
        """Test if API Key is loaded correctly."""
        print(f"\n[Check] Verifying API Key...")
        self.assertIsNotNone(self.api_key, "FAIL: OPENAI_API_KEY is missing in .env")
        self.assertTrue(len(self.api_key) > 20, "FAIL: API Key looks too short to be valid.")
        print("PASS: API Key found.")

    def test_02_database_exists(self):
        """Test if the specific database file exists."""
        print(f"[Check] Verifying Database file: {self.test_db_path}...")
        
        # Check if directory exists
        db_dir = os.path.dirname(self.test_db_path)
        if db_dir and not os.path.exists(db_dir):
            self.fail(f"FAIL: Directory '{db_dir}' does not exist.")
            
        # Check if file exists (Optional: Create a dummy file if testing logic only)
        if not os.path.exists(self.test_db_path):
             print(f"SKIPPING: Database {self.test_db_path} not found. Ensure you download it first.")
        else:
            self.assertTrue(os.path.exists(self.test_db_path), "FAIL: Database file not found.")
            print("PASS: Database file exists.")

    def test_03_response_parsing(self):
        """Unit test for the response parsing logic."""
        print("[Check] Testing response parsing logic...")
        
        # Case A: Legacy LangChain
        resp_a = {"output": "The answer is 42."}
        self.assertEqual(_mock_extract_output(resp_a), "The answer is 42.")
        
        # Case B: Modern LangGraph (Dict with messages)
        class MockMsg:
            content = "Graph answer"
        resp_b = {"messages": [MockMsg()]}
        self.assertEqual(_mock_extract_output(resp_b), "Graph answer")
        
        # Case C: Direct String
        resp_c = "Direct answer"
        self.assertEqual(_mock_extract_output(resp_c), "Direct answer")
        print("PASS: Response parsing logic works.")

    def test_04_agent_build_and_run(self):
        """Integration Test: Build agent and run a dummy query."""
        if not build_agent:
            print("SKIPPING: Agent module not found.")
            return
        
        if not self.api_key:
            print("SKIPPING: No API Key available for live test.")
            return

        if not os.path.exists(self.test_db_path):
            print("SKIPPING: No database available for live test.")
            return

        print(f"[Check] LIVE TEST: Initializing Agent with {self.test_db_path}...")
        
        try:
            agent = build_agent(
                api_key=self.api_key,
                temperature=0,
                model="gpt-4o",  # or gpt-3.5-turbo
                db_path=self.test_db_path
            )
            self.assertIsNotNone(agent, "FAIL: Agent object is None")
            
            # Run a very cheap/fast query
            prompt = "List the table names in the database. Return as a comma separated list."
            print(f"Sending Prompt: '{prompt}'")
            
            # Handle invocation (simplified for test)
            if hasattr(agent, 'invoke'):
                response = agent.invoke({"input": prompt})
            else:
                response = agent(prompt)
                
            output = _mock_extract_output(response)
            
            print(f"Agent Reply: {output}")
            self.assertTrue(len(output) > 0, "FAIL: Agent returned empty response.")
            print("PASS: Agent is functional.")
            
        except Exception as e:
            self.fail(f"FAIL: Agent crashed during execution. Error: {e}")


if __name__ == "__main__":
    # Custom runner to make output cleaner
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDataAnalysisAgent)
    unittest.TextTestRunner(verbosity=0).run(suite)