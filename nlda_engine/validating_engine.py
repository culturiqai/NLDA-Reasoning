# nlda_engine/validating_engine.py

"""
An extension of the Nalanda Engine that incorporates the Reality Filter
to test and validate new, unverified knowledge.
"""

from typing import Type

from .engine import NalandaEngine
from .filter import RealityFilter
from .language_interface import LanguageInterface
from .knowledge_store import KnowledgeStore

class ValidatingNalandaEngine(NalandaEngine):
    """
    This engine inherits the core reasoning and cultural learning capabilities
    of the base NalandaEngine and adds the crucial final step of hypothesis
    validation.
    """
    def __init__(self, language_interface: Type[LanguageInterface], initial_schemas: dict = None):
        """
        Initializes the ValidatingNalandaEngine.

        Args:
            language_interface (Type[LanguageInterface]): An instance of the language interface.
            initial_schemas (dict, optional): A dictionary of initial schemas. Defaults to None.
        """
        # Initialize the base engine first
        super().__init__(language_interface, initial_schemas)
        
        # Now, add the Reality Filter component
        self.filter = RealityFilter(self.logic, self.sandbox)
        print("   -> Upgraded to ValidatingNalandaEngine with Reality Filter.")

        # Immediately run the Genesis Validation cycle
        self.self_reflect()

    def self_reflect(self) -> None:
        """
        The Genesis Validation Cycle.
        The engine tests its own foundational beliefs against the Sandbox
        and corrects them if they are found to be flawed.
        """
        print("\\n" + "="*50)
        print("      STARTING GENESIS VALIDATION (SELF-REFLECTION)")
        print("="*50)

        all_schemas = self.knowledge_store.get_all_schemas(include_properties=True)
        
        for name, schema_data in all_schemas.items():
            # The schema data needs the 'name' for the test function
            if 'name' not in schema_data:
                 schema_data['name'] = name
            
            test_results = self.filter.test_hypothesis(schema_data)
            
            if not test_results['is_consistent'] and test_results['prediction'] != 'N/A':
                # A core belief is wrong. Trigger the learning cycle.
                print(f"[REFLECT] Found contradiction in core belief: '{name}'.")
                
                # This is a simplification. A real system would have a more complex
                # "credit assignment" process. For now, we assume 'is_brittle' is the issue.
                is_brittle_in_reality = "shatter" in test_results['reality']
                self._learn(name, 'is_brittle', is_brittle_in_reality)

        print("\\n" + "="*50)
        print("                GENESIS VALIDATION COMPLETE")
        print("="*50)

    def assimilate_topic(self, topic: str) -> None:
        """
        Orchestrates the "Cultural Learning" process for a single topic using RAG.

        Args:
            topic (str): The topic to learn about (e.g., "porcelain doll").
        """
        # Use the language interface to get a new schema from the topic
        new_schema = self.language_interface.extract_schema_from_topic(topic)

        # The LLM now returns the schema directly, including the slug-ified name
        # We need to handle the case where the key might be missing
        if not new_schema or 'properties' not in new_schema:
             print(f"[ASSIMILATE] Could not generate a valid schema for topic: {topic}")
             return

        # Let's create the name from the topic itself for consistency
        schema_name = topic.lower().replace(" ", "_")

        # Check if schema already exists to avoid overwriting verified knowledge
        if self.knowledge_store.get_schema(schema_name):
            print(f"[ASSIMILATE] Schema '{schema_name}' already exists. Skipping.")
            return

        self.knowledge_store.add_schema(schema_name, new_schema, verified=False)
        print(f"[ASSIMILATE] Assimilation complete. New unverified schema '{schema_name}' added.")

    def validate_hypotheses(self) -> None:
        """
        Orchestrates the "Reality Filter" process.
        Tests all unverified schemas and promotes the ones that are consistent.
        """
        print("\\n" + "="*50)
        print("      STARTING VALIDATION OF UNVERIFIED HYPOTHESES")
        print("="*50)

        unverified_schemas = {
            name: data for name, data in self.knowledge_store.get_all_schemas(include_properties=True).items()
            if not data.get('verified')
        }

        if not unverified_schemas:
            print("[VALIDATE] No unverified schemas to test.")
            return

        print(f"[VALIDATE] Found {len(unverified_schemas)} unverified schemas to test.")
        
        for name, schema_data in unverified_schemas.items():
            # The schema data needs the 'name' for the test function
            schema_data['name'] = name
            test_results = self.filter.test_hypothesis(schema_data)
            if test_results['is_consistent']:
                # If the hypothesis holds up to scrutiny, verify it.
                self.knowledge_store.verify_schema(name)
            else:
                # In a more advanced system, we might try to correct the schema
                # or add it to a "rejected" list. For now, we just report.
                print(f"[VALIDATE] Schema '{name}' was found to be inconsistent and will remain unverified.")
        
        print("\\n" + "="*50)
        print("                VALIDATION CYCLE COMPLETE")
        print("="*50)

    def reason_about_tool_use(self, scene_data: dict) -> dict:
        """
        The core reasoning cycle for a tool-use event.

        Args:
            scene_data (dict): The structured data from the PerceptualEngine.
        
        Returns:
            dict: A dictionary with the results of the cycle.
        """
        tool_name = scene_data.get('norm_tool')
        target_name = scene_data.get('norm_target')

        if not tool_name or not target_name:
            return {"error": "Could not identify both a tool and a target in the scene."}

        print(f"\\n--- Reasoning about tool use: {tool_name} on {target_name} ---")

        tool_schema = self.knowledge_store.get_schema(tool_name)
        target_schema = self.knowledge_store.get_schema(target_name)

        if not tool_schema or not target_schema:
            return {"error": "Could not retrieve schemas for both tool and target."}

        # 1. PREDICT
        prediction = self.logic.predict_tool_use_outcome(tool_schema, target_schema)
        print(f"   -> My Prediction: '{prediction}'")

        # 2. EXPERIENCE
        reality = self.sandbox.get_tool_use_ground_truth(tool_schema, target_schema)
        print(f"   -> Ground Truth from Sandbox: '{reality}'")
        
        # 3. COMPARE
        consistent = (prediction == reality)
        print(f"   -> Consistent: {consistent}")
        
        # The _learn cycle would need to be upgraded to handle credit assignment
        # for these more complex interactions. For now, we just report.
        
        return {
            "prediction": prediction,
            "reality": reality,
            "consistent": consistent
        }
