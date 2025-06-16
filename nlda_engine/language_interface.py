# nlda_engine/language_interface.py

"""
The Language Interface: The Engine's Connection to the World of Words.
This module handles all interactions with the Large Language Model (LLM),
including RAG-based knowledge extraction, perception parsing, and mimicry.
"""
import sys
import os
import json
import re
import ollama # Use the direct ollama library

# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .vector_db import VectorDB

class LanguageInterface:
    """
    Manages all communication with the Language Model.
    This has been refactored to use the 'ollama' library for stability.
    """
    def __init__(self, model_name: str = "phi3:latest", corpus_path: str = "corpus/"):
        self.model_name = model_name
        self.client = self._initialize_client()
        self.vector_db = _create_vector_db(corpus_path) if os.path.exists(corpus_path) else None
        if not self.vector_db:
             print("Warning: LanguageInterface is operating without a functional VectorDB.")

    def _initialize_client(self):
        """Initializes the connection to the Ollama client."""
        try:
            # The ollama library automatically finds the running server.
            ollama.list() 
            print(f"[Ollama] Successfully connected to Ollama client. Using model: '{self.model_name}'")
            return ollama
        except Exception as e:
            print(f"Fatal: Could not connect to Ollama. Is the Ollama server running? Error: {e}")
            return None

    def _generate_response(self, prompt: str, temperature=0.0, format_json=False) -> str:
        """A central method to interact with the LLM API using Ollama."""
        if not self.client:
            return "Ollama client not initialized."
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                format='json' if format_json else '',
                options={'temperature': temperature}
            )
            return response['message']['content']
        except Exception as e:
            print(f"[Ollama] Error during generation: {e}")
            return ""
            
    def extract_schema_from_topic(self, topic: str) -> dict:
        """
        Uses RAG and the LLM to extract a structured schema for a given topic.
        """
        print(f"\n[RAG] Received topic to extract schema for: '{topic}'")
        if not self.vector_db:
            return None
        context = self.vector_db.search(topic)
        prompt = self._get_schema_prompt(topic, context)
        
        # Use Ollama's built-in JSON mode for reliable output
        response_str = self._generate_response(prompt, format_json=True)
        if not response_str:
            return None
        
        try:
            # The 'json' format guarantees the response is a parsable string
            parsed_schema = json.loads(response_str)
            
            # Still, it's good practice to keep defensive cleanup
            if 'properties' in parsed_schema and isinstance(parsed_schema['properties'], dict):
                for key, value in parsed_schema['properties'].items():
                    if isinstance(value, list) and len(value) > 0:
                        parsed_schema['properties'][key] = value[0]
            
            return parsed_schema
        except json.JSONDecodeError:
            print(f"[LLM] Failed to decode supposedly valid JSON from Ollama: {response_str}")
            return None

    def get_raw_prediction(self, prompt: str) -> str:
        """
        Gets a raw, direct prediction from the LLM to act as the 'Mimic'.
        """
        return self._generate_response(prompt, temperature=0.2)

    def query_for_json(self, prompt: str) -> dict:
        """
        A generic method to query the LLM and expect a JSON object in return.
        """
        response_str = self._generate_response(prompt, format_json=True)
        if not response_str:
            return None
        try:
            return json.loads(response_str)
        except json.JSONDecodeError:
            print(f"[LLM] Failed to decode supposedly valid JSON from Ollama: {response_str}")
            return None

    def _get_schema_prompt(self, topic: str, context: str) -> str:
        """Creates the prompt for the LLM to generate a schema for a topic."""
        return (
            f"From the context below, extract properties for the topic '{topic}' into a JSON object. "
            "Your response MUST only be the JSON object. "
            "The object must have an 'is_a' key and a 'properties' object. "
            "Include physical constants like 'specific_heat_capacity_J_per_kg_C', "
            "'latent_heat_of_fusion_J_per_kg', 'density_kg_per_m3', and 'volume_m3' if they are present. "
            "Example: {{\"is_a\": \"substance\", \"properties\": {{\"specific_heat_capacity_J_per_kg_C\": 4186}} }}\\n\\n"
            f"CONTEXT: '''{context}'''\\n\\n"
            f"JSON for '{topic}':"
        )

# This part remains unchanged as it's for initializing the VectorDB
def _create_vector_db(corpus_path: str) -> VectorDB:
    """Helper function to initialize the VectorDB."""
    db = VectorDB()
    if not db.index:
        print("[VectorDB] Building new vector index from corpus...")
        docs = db.load_documents(corpus_path)
        chunks = db.chunk_documents(docs)
        db.build_index(chunks)
    else:
        print("[VectorDB] Loaded existing vector index.")
    return db

if __name__ == '__main__':
    # A simple test to verify Ollama connection and functionality
    li = LanguageInterface()
    if li.client:
        print("\n--- Testing Raw Prediction ---")
        raw_pred = li.get_raw_prediction("Why is the sky blue?")
        print(f"  -> Prediction: {raw_pred}")

        print("\n--- Testing JSON Query ---")
        json_q = li.query_for_json("Create a JSON object for a user with name 'John' and age 30.")
        print(f"  -> JSON: {json_q}")

    else:
        print("Could not run tests because the language model client failed to initialize.") 