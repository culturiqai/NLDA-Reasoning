"""
The Central Orchestrator for the Nalanda Engine.
This class integrates all components and manages the main reasoning
and learning cycles.
"""

import copy
from typing import Type

from .knowledge_store import KnowledgeStore
from .sandbox import Sandbox
from .components import LogicEngine
from .proposer import HypothesisProposer
from .language_interface import LanguageInterface


class NalandaEngine:
    """
    An AGI architecture that integrates perception, reasoning, and learning.
    """
    def __init__(self, language_interface: Type[LanguageInterface], initial_schemas: dict = None):
        print("--- Initializing Nalanda Engine ---")
        self.language_interface = language_interface
        # The engine now manages a KnowledgeStore object instead of a raw dictionary.
        self.knowledge_store = KnowledgeStore(initial_schemas)
        self.logic = LogicEngine()
        self.sandbox = Sandbox()
        # The proposer needs the language interface to function
        self.proposer = HypothesisProposer(language_interface)
        print("   -> Engine initialized with a graph-based worldview and Hypothesis Proposer.")

    def get_belief(self, object_type: str) -> dict:
        """Helper to show current knowledge by querying the graph."""
        schema = self.knowledge_store.get_schema(object_type)
        return schema.get('properties', {}) if schema else {}

    def _learn(self, object_type: str, property_to_change: str, correct_value: bool) -> str:
        """
        The "Great Unfolding" cycle. Modifies the KnowledgeStore graph
        based on a conflict between prediction and reality.
        """
        print("\n[LEARN] Conflict detected between prediction and reality!")
        print(f"   -> Updating core belief about '{object_type}'.")
        
        self.knowledge_store.update_property(object_type, property_to_change, correct_value)
        
        print(f"   -> Successfully updated '{property_to_change}' to '{correct_value}'. The 'seed' has ripened.")
        return f"Updated belief about '{object_type}': '{property_to_change}' is now '{correct_value}'."

    def assimilate_text(self, text_content: str):
        """
        Orchestrates the "Cultural Learning" process.
        1. Proposes new schemas from text.
        2. Adds them to the KnowledgeStore as unverified.
        """
        # Use the proposer to get new schemas from the text
        new_schemas = self.proposer.propose_from_text(text_content)

        if not new_schemas:
            print("[ASSIMILATE] No new schemas were proposed.")
            return

        # Add the new schemas to the knowledge store as unverified beliefs
        for name, data in new_schemas.items():
            # Check if schema already exists to avoid overwriting verified knowledge
            if self.knowledge_store.get_schema(name):
                print(f"[ASSIMILATE] Schema '{name}' already exists. Skipping.")
                continue
            self.knowledge_store.add_schema(name, data, verified=False)
        
        print(f"[ASSIMILATE] Assimilation complete. {len(new_schemas)} new unverified schemas added.")

    def reason_about_object(self, object_type: str) -> dict:
        """
        The core reasoning cycle for a single object.
        This is a simplified entry point for the demo.
        It returns a dictionary with the results of the cycle.
        """
        print(f"\n--- Reasoning about object: {object_type} ---")
        
        # 1. ACTIVATE: Get the current belief state from the knowledge store
        current_object_state = self.knowledge_store.get_schema(object_type)
        if not current_object_state:
            error_msg = f"No schema found for object: {object_type}"
            return {"error": error_msg}

        # 2. PREDICT: Use the logic engine to predict an outcome
        prediction = self.logic.predict(current_object_state)
        print(f"   -> My Prediction: '{prediction}'")
        
        # 3. EXPERIENCE (Ground Truth): Check what *really* happens in the sandbox
        reality = self.sandbox.get_ground_truth(current_object_state)
        print(f"   -> Ground Truth from Sandbox: '{reality}'")
        
        # 4. LEARN: If prediction was wrong, trigger the learning cycle
        consistent = (prediction == reality)
        learning_summary = "Beliefs are consistent with reality. No update needed."
        if not consistent:
            # This is a simplification. A real system would have a more complex
            # "credit assignment" process to figure out *which* property was wrong.
            is_brittle_in_reality = "shatter" in reality
            learning_summary = self._learn(object_type, 'is_brittle', is_brittle_in_reality)
        else:
            print("[LEARN] Prediction matched reality. Beliefs reinforced.")
        
        return {
            "prediction": prediction,
            "reality": reality,
            "consistent": consistent,
            "learning_summary": learning_summary
        } 