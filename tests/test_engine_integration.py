import unittest
import sys
import os

# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlda_engine.validating_engine import ValidatingNalandaEngine
from nlda_engine.knowledge_store import INITIAL_SCHEMAS
from nlda_engine.language_interface import LanguageInterface

class TestEngineIntegration(unittest.TestCase):
    """
    Integration test for the full ValidatingNalandaEngine,
    ensuring all components work together correctly, especially
    the Genesis Validation (self-correction) cycle.
    """

    def test_genesis_validation_and_self_correction(self):
        """
        Tests the entire engine initialization process, verifying that
        the engine self-corrects its initial flawed beliefs.
        """
        print("\\n--- Running Engine Integration Test ---")
        
        # 1. SETUP: Initialize the Language Interface and the Engine
        lang_interface = LanguageInterface()
        # A basic check to ensure the LLM client connected before running the test
        self.assertIsNotNone(lang_interface.client, "Language Interface client could not be initialized.")

        # Check the initial state of the core belief before the engine runs
        initial_belief = INITIAL_SCHEMAS['rubber_ball']['properties']['is_brittle']
        print(f"Initial belief for 'rubber_ball' -> is_brittle: {initial_belief}")
        self.assertTrue(initial_belief, "Test precondition failed: Initial belief should be flawed (True).")

        # 2. EXECUTION: Initialize the engine, which automatically triggers self-reflection
        engine = ValidatingNalandaEngine(lang_interface, INITIAL_SCHEMAS)

        # 3. VERIFICATION: Check the knowledge store *after* initialization
        corrected_belief = engine.knowledge_store.get_schema('rubber_ball')['properties']['is_brittle']
        print(f"Corrected belief for 'rubber_ball' -> is_brittle: {corrected_belief}")
        self.assertFalse(corrected_belief, "Engine failed to self-correct the flawed belief.")
        
        # Also check another belief to ensure it wasn't changed
        glass_belief = engine.knowledge_store.get_schema('glass_bottle')['properties']['is_brittle']
        self.assertTrue(glass_belief, "Engine incorrectly modified a correct belief.")
        
        print("--- Engine Integration Test Passed ---")

if __name__ == '__main__':
    unittest.main() 