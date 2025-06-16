# nlda_engine/components.py

"""
Core Reasoning Components of the Nalanda Engine
"""
from .language_interface import LanguageInterface
import re
import json

class PerceptualEngine:
    """
    Represents the Mano-vijñāna (Mental Consciousness).
    Uses a Language Model to parse natural language into structured scene descriptions.
    """
    def __init__(self, language_interface: LanguageInterface):
        self.language_interface = language_interface

    def _get_perceptual_prompt(self, text: str) -> str:
        """Creates the prompt for the LLM to parse a simple event."""
        return (
            "You are a parsing engine. Your task is to analyze a sentence and extract event components into a valid JSON object. "
            "You must ONLY return the JSON object. Do not add any extra text, commentary, or explanations. "
            "The valid JSON keys are 'actor', 'action', 'object', and 'target'. "
            "If a component is not present in the sentence, its value must be null.\\n\\n"
            "--- EXAMPLE ---\\n"
            "SENTENCE: 'The ball is on the table.'\\n"
            "VALID JSON ONLY: {{\"actor\": null, \"action\": \"is on\", \"object\": \"The ball\", \"target\": \"the table\"}}\\n"
            "--- END EXAMPLE ---\\n\\n"
            f"SENTENCE: '''{text}'''\\n"
            "VALID JSON ONLY:"
        )

    def _get_tool_use_prompt(self, text: str) -> str:
        """Creates the prompt for the LLM to parse a tool-use event."""
        return (
            "You are a parsing engine. Your task is to analyze a sentence and extract event components into a valid JSON object. "
            "You must ONLY return the JSON object. Do not add any extra text, commentary, or explanations. "
            "The valid JSON keys are 'actor', 'action', 'tool', and 'target_object'. "
            "If a component is not present in the sentence, its value must be null.\\n\\n"
            "--- EXAMPLE ---\\n"
            "SENTENCE: 'A chef chops a carrot with a kitchen knife.'\\n"
            "VALID JSON ONLY: {{\"actor\": \"A chef\", \"action\": \"chops\", \"tool\": \"a kitchen knife\", \"target_object\": \"a carrot\"}}\\n"
            "--- END EXAMPLE ---\\n\\n"
            f"SENTENCE: '''{text}'''\\n"
            "VALID JSON ONLY:"
        )

    def parse_text_input(self, text: str) -> dict:
        """
        Uses the LanguageInterface to parse a text input into a structured event.
        Then, it extracts the primary object to activate a knowledge schema.
        """
        print(f"\\n[PERCEIVE] Received text: '{text}'")
        event_data = self.language_interface.parse_event_from_text(text)
        print(f"[PERCEIVE] Parsed event data: {event_data}")
        
        if "error" in event_data or not event_data.get("object"):
            print("[PERCEIVE] Error parsing text or object not found in event.")
            return None
        
        # Normalize the object name to match knowledge store keys (e.g., "rubber ball" -> "rubber_ball")
        object_name = event_data.get("object")
        normalized_object_name = object_name.lower().replace(" ", "_")
        print(f"[PERCEIVE] Normalized object of interest to: '{normalized_object_name}'")

        # The 'object' from the parsed event becomes the key for our scene.
        # This is a simplification; a real system would handle multiple objects.
        return {
            'type': 'interaction',
            'object_of_interest': normalized_object_name
        }

    def parse_tool_use_text(self, text_input: str) -> dict:
        """
        Parses a more complex sentence describing a tool being used.

        Args:
            text_input (str): The sentence to parse.
        
        Returns:
            dict: A structured dictionary of the event.
        """
        print(f"\\n[PERCEIVE] Received tool-use text: '{text_input}'")
        prompt = self._get_tool_use_prompt(text_input)
        parsed_event = self.language_interface.query_for_json(prompt)
        
        if parsed_event:
            # First, normalize the object names to match schema keys
            parsed_event['norm_target'] = self._normalize_object_name(parsed_event.get('target_object', ''))
            parsed_event['norm_tool'] = self._normalize_object_name(parsed_event.get('tool', ''))
            print(f"[PERCEIVE] Parsed tool-use event: {parsed_event}")
            return parsed_event
            
        return None

    def _normalize_object_name(self, name_str: str) -> str:
        """Converts a natural language name to a schema-compatible key."""
        # e.g., "a porcelain piggy bank" -> "a_porcelain_piggy_bank"
        # This is a simple version; a real one would be more robust.
        return name_str.lower().replace(" ", "_")

class LogicEngine:
    """
    Represents Pramāṇa-vāda (The Doctrine of Valid Cognition).
    It uses formal rules to infer causal outcomes based on its current beliefs.
    This version is upgraded for v0.3 to perform more quantitative reasoning.
    """
    def _calculate_impact_force(self, mass_kg, drop_height=2.0, gravity=9.8):
        """A simplified physics calculation."""
        # E = mgh -> v = sqrt(2gh) -> p = mv. Force is complex, we use momentum as proxy.
        potential_energy = mass_kg * gravity * drop_height
        # Simplified proxy for impact force
        return potential_energy * 10 

    def predict(self, object_state: dict) -> str:
        """
        Predicts an outcome based on a calculated impact force and believed properties.
        """
        properties = object_state.get('properties', {})
        is_brittle = properties.get('is_brittle', False)
        mass_kg = properties.get('mass_kg', 1.0)
        object_name = object_state.get('name', 'object')

        # Perform internal calculation
        estimated_impact = self._calculate_impact_force(mass_kg)
        shatter_threshold = 15.0 # The engine's internal belief about the shatter threshold

        print(f"[PREDICT] Based on current belief (is_brittle: {is_brittle}) and estimated impact ({estimated_impact:.2f})...")
        
        if is_brittle and estimated_impact > shatter_threshold:
            return f"The {object_name} will shatter."
        else:
            return f"The {object_name} will bounce."

    def reason_about_tool_use(self, event: dict, knowledge: 'KnowledgeStore'):
        """
        Reasons about the outcome of a tool being used on a target object.
        """
        print(f"\\n--- Reasoning about tool use: {event['norm_tool']} on {event['norm_target']} ---")
        
        tool_key_norm = re.sub(r'^(a_|an_)', '', event['norm_tool'])
        target_key_norm = re.sub(r'^(a_|an_)', '', event['norm_target'])

        # Flexible schema matching
        tool_schema = None
        target_schema = None
        tool_key_final = None
        target_key_final = None

        all_schemas = knowledge.get_all_schemas(include_properties=True)
        
        for key in all_schemas:
            if key in tool_key_norm:
                tool_schema = all_schemas[key]
                tool_key_final = key
            if key in target_key_norm:
                target_schema = all_schemas[key]
                target_key_final = key

        if not tool_schema or not target_schema:
            print("[NLDA] Reasoning failed: Could not retrieve schemas for both tool and target.")
            return

        # Core physical reasoning
        tool_props = tool_schema.get('properties', {})
        target_props = target_schema.get('properties', {})

        tool_mass = tool_props.get('mass_kg', 0.1)
        target_brittle = target_props.get('is_brittle', False)

        # Simplified logic: if target is brittle and tool has sufficient mass, it breaks.
        if target_brittle and tool_mass > 0.2:
            print(f"[NLDA] The {target_key_final} is brittle and the {tool_key_final} is heavy enough.")
            print("  -> NLDA Prediction: The piggy bank will shatter.")
        else:
            print(f"[NLDA] The {target_key_final} may not be brittle or the {tool_key_final} is too light.")
            print("  -> NLDA Prediction: The piggy bank will not shatter.")

class ReportingEngine:
    """
    The "Skilled Communicator".
    Uses the Language Model to generate human-readable reports about the engine's
    thought process and learning outcomes.
    """
    def __init__(self, language_interface: LanguageInterface):
        self.language_interface = language_interface

    def generate_report(self, prediction, reality, consistent, learning_summary):
        """
        Generates a narrative report of the engine's full operational cycle.
        """
        return self.language_interface.generate_report(
            prediction, reality, consistent, learning_summary
        ) 