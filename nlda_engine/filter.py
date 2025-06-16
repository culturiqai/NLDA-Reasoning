"""
The Reality Filter (Madhyamaka) Component of the Nalanda Engine.
This module is responsible for testing unverified hypotheses against
the simulated reality of the Sandbox.
"""

class RealityFilter:
    """
    Designs and executes experiments to validate or reject unverified beliefs.
    It acts as the gatekeeper for all new knowledge.
    """
    def __init__(self, logic_engine, sandbox):
        self.logic_engine = logic_engine
        self.sandbox = sandbox
        print("[RealityFilter] Initialized.")

    def test_hypothesis(self, schema: dict) -> dict:
        """
        Tests a single unverified schema. For now, the test is a simple
        "drop test" to check the 'is_brittle' property.

        Returns:
            dict: A dictionary containing the results of the test:
                  {'is_consistent': bool, 'prediction': str, 'reality': str}
        """
        schema_name = schema.get('name', 'untitled_schema')
        print(f"\\n[FILTER] Testing hypothesis for: '{schema_name}'")
        
        properties = schema.get('properties', {})
        if 'is_brittle' not in properties:
            print(f"[FILTER] Schema '{schema_name}' lacks 'is_brittle' property. Cannot perform drop test. Skipping.")
            # Return a neutral result if the test is not applicable
            return {'is_consistent': True, 'prediction': 'N/A', 'reality': 'N/A'}

        # 1. PREDICT: Based on the unverified belief.
        prediction = self.logic_engine.predict(schema)
        print(f"[FILTER]   -> Prediction based on hypothesis: '{prediction}'")

        # 2. EXPERIENCE: Run the simulation in the sandbox for ground truth.
        reality = self.sandbox.get_ground_truth(schema)
        print(f"[FILTER]   -> Ground truth from Sandbox: '{reality}'")

        # 3. COMPARE: Check if the prediction matched reality.
        is_consistent = (prediction == reality)
        if is_consistent:
            print(f"[FILTER]   -> RESULT: Hypothesis for '{schema_name}' is consistent with reality.")
        else:
            print(f"[FILTER]   -> RESULT: Contradiction found for '{schema_name}'. Hypothesis is flawed.")
            
        return {'is_consistent': is_consistent, 'prediction': prediction, 'reality': reality}