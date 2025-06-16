"""
The Hypothesis Proposer Component of the Nalanda Engine
"""
from .language_interface import LanguageInterface

class HypothesisProposer:
    """
    The "Cultural Learning" module.
    Uses the Language Model to read unstructured text and propose new,
    unverified schemas for the KnowledgeStore. This is the engine for
    autonomous knowledge acquisition.
    """
    def __init__(self, language_interface: LanguageInterface):
        self.language_interface = language_interface

    def propose_from_text(self, text: str) -> dict:
        """
        Generates a dictionary of new, potential schemas from a block of text.
        """
        print("\\n[PROPOSE] Reading text to propose new knowledge schemas...")
        proposed_schemas = self.language_interface.extract_schemas_from_text(text)
        
        if 'error' in proposed_schemas or not proposed_schemas:
            print("[PROPOSE] Failed to extract schemas from text.")
            return {}
            
        print(f"[PROPOSE] Successfully proposed {len(proposed_schemas)} new schemas.")
        return proposed_schemas 