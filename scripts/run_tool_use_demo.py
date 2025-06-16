# scripts/run_tool_use_demo.py

"""
Demonstration for Phase 3: Simple Tool Use.
This script showcases the engine's ability to reason about a complex event
involving multiple objects and contrasts it with a pure LLM 'Mimic'.
"""
import sys
import os
import json

# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlda_engine.validating_engine import ValidatingNalandaEngine
from nlda_engine.knowledge_store import INITIAL_SCHEMAS
from nlda_engine.language_interface import LanguageInterface
from nlda_engine.components import PerceptualEngine, LogicEngine

def print_knowledge_store(engine: ValidatingNalandaEngine, title: str):
    """Helper function to print the knowledge store in a readable format."""
    print("\\n" + "="*50)
    print(f"      {title.upper()}")
    print("="*50)
    all_schemas = engine.knowledge_store.get_all_schemas(include_properties=True)
    print(json.dumps(all_schemas, indent=2))
    print("="*50 + "\\n")

def main():
    """Main function to run the tool use demonstration."""
    print("--- Initializing NLDA v1.1 Tool-Use Demo ---")
    
    lang_interface = LanguageInterface()
    if not lang_interface.client:
        print("Fatal: Could not initialize Language Interface.")
        return
        
    engine = ValidatingNalandaEngine(lang_interface, INITIAL_SCHEMAS)
    perceptual_engine = PerceptualEngine(lang_interface)
    logic_engine = LogicEngine()
    
    # --- Show initial state after self-correction ---
    print_knowledge_store(engine, "Knowledge Store After Genesis Validation")

    # --- Step 1: Learn about the objects involved from the corpus ---
    print("--- Step 1: Assimilating knowledge about tools and containers ---")
    engine.assimilate_topic("toy hammer")
    engine.assimilate_topic("piggy bank")
    print_knowledge_store(engine, "Knowledge Store After Assimilation")
    
    # --- Step 2: Validate all new hypotheses ---
    print("--- Step 2: Validating new hypotheses against the Sandbox ---")
    engine.validate_hypotheses()
    print_knowledge_store(engine, "Knowledge Store After Validation")

    # --- Step 3: Define the scenario and query the 'Mimic' ---
    scenario = "A person strikes a porcelain piggy bank with a toy hammer."
    print(f"--- Step 3: Reasoning about the scenario: '{scenario}' ---")
    
    print("\\n" + "-"*20 + " The Mimic's Turn " + "-"*20)
    mimic_prompt = (
        "Based on general knowledge, what is the most likely outcome of the following event? "
        "Describe only the physical result. Do not add any conversational filler or commentary.\\n\\n"
        f"Event: {scenario}"
    )
    mimic_prediction = lang_interface.get_raw_prediction(mimic_prompt)
    print(f"The Mimic (raw LLM) predicts: '{mimic_prediction}'")
    print("-" * 58 + "\\n")
    
    # --- Step 4: The Nalanda Engine's Turn ---
    print("-" * 20 + " The NLDA's Turn " + "-"*22)
    
    scene_data = perceptual_engine.parse_tool_use_text(scenario)
    
    if not scene_data or not scene_data.get('norm_tool') or not scene_data.get('norm_target'):
        print("[NLDA] Failed to parse the tool-use scenario.")
    else:
        # Pass the knowledge store from the main engine to the logic engine
        logic_engine.reason_about_tool_use(scene_data, engine.knowledge_store)

    print("-" * 58 + "\\n")
    
    print("--- Tool-Use Demo Complete ---")


if __name__ == "__main__":
    main() 