# scripts/run_rag_demo.py

"""
The final demonstration for the Nalanda Engine v0.10.
This script showcases the RAG-powered, topic-based learning and validation cycle.
"""
import sys
import os
import json

# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlda_engine.validating_engine import ValidatingNalandaEngine
from nlda_engine.knowledge_store import INITIAL_SCHEMAS
from nlda_engine.language_interface import LanguageInterface
from nlda_engine.components import PerceptualEngine

def print_knowledge_store(engine: ValidatingNalandaEngine, title: str):
    """Helper function to print the knowledge store in a readable format."""
    print("\\n" + "="*50)
    print(f"      {title.upper()}")
    print("="*50)
    all_schemas = engine.knowledge_store.get_all_schemas(include_properties=True)
    print(json.dumps(all_schemas, indent=2))
    print("="*50 + "\\n")

def main():
    """Main function to run the demonstration."""
    print("--- Initializing NLDA v0.10 RAG Demo ---")
    
    lang_interface = LanguageInterface()
    if not lang_interface.client or not lang_interface.vector_db.index:
        print("Fatal: Could not initialize Language Interface or VectorDB.")
        return
        
    engine = ValidatingNalandaEngine(lang_interface, INITIAL_SCHEMAS)
    perceptual_engine = PerceptualEngine(lang_interface)
    
    # --- Show initial state ---
    print_knowledge_store(engine, "Knowledge Store After Genesis Validation")

    # --- Step 1: Learn about a specific topic using RAG ---
    topic_to_learn = "porcelain doll"
    print(f"--- Step 1: Assimilating knowledge about '{topic_to_learn}' ---")
    engine.assimilate_topic(topic_to_learn)
    print_knowledge_store(engine, "Knowledge Store After Assimilating 'Porcelain Doll'")

    # --- Step 2: Validate all new hypotheses ---
    print("--- Step 2: Validating new hypotheses against the Sandbox ---")
    engine.validate_hypotheses()
    print_knowledge_store(engine, "Knowledge Store After Validation")

    # --- Step 3: Use the newly verified knowledge ---
    print("--- Step 3: Grounded reasoning with newly verified knowledge ---")
    
    new_event_text = "A porcelain doll is dropped on the floor."
    scene_data = perceptual_engine.parse_text_input(new_event_text)
    
    if scene_data and scene_data.get('object_of_interest'):
        object_of_interest = scene_data['object_of_interest']
        
        print(f"\\nInitial Belief about '{object_of_interest}': {engine.get_belief(object_of_interest)}")
        
        results = engine.reason_about_object(object_of_interest)
        
        if 'error' in results:
            print(f"Reasoning failed: {results['error']}")
        else:
            print(f"Prediction: {results['prediction']}")
            print(f"Reality: {results['reality']}")
            print(f"Conclusion: Belief was {'consistent' if results['consistent'] else 'inconsistent'} with reality.")
    else:
        print("[DEMO] Failed to parse the final event.")

    print("\\n" + "="*50)
    print("                   RAG DEMO COMPLETE")
    print("="*50)

if __name__ == "__main__":
    main()
