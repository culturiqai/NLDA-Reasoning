import unittest
import sys
import os

# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlda_engine.knowledge_store import KnowledgeStore, INITIAL_SCHEMAS

class TestKnowledgeStore(unittest.TestCase):
    """Unit tests for the KnowledgeStore class."""

    def setUp(self):
        """Set up a new KnowledgeStore for each test."""
        self.ks = KnowledgeStore(INITIAL_SCHEMAS)

    def test_initialization(self):
        """Test that the knowledge store is initialized correctly."""
        self.assertIsNotNone(self.ks.graph)
        self.assertTrue(self.ks.graph.has_node('rubber_ball'))
        self.assertEqual(
            self.ks.get_schema('rubber_ball')['properties']['is_brittle'],
            True
        )

    def test_add_and_get_schema(self):
        """Test adding a new schema and retrieving it."""
        new_schema = {
            "is_a": "physical_object",
            "properties": {"material": "wood", "mass_kg": 0.5}
        }
        self.ks.add_schema("wooden_block", new_schema, verified=True)
        
        retrieved_schema = self.ks.get_schema("wooden_block")
        self.assertIsNotNone(retrieved_schema)
        self.assertEqual(retrieved_schema['properties']['material'], 'wood')
        self.assertTrue(retrieved_schema['verified'])

    def test_get_nonexistent_schema(self):
        """Test that getting a nonexistent schema returns None."""
        self.assertIsNone(self.ks.get_schema("nonexistent_item"))

    def test_update_property(self):
        """Test updating a property of an existing schema."""
        self.ks.update_property('rubber_ball', 'is_brittle', False)
        updated_schema = self.ks.get_schema('rubber_ball')
        self.assertFalse(updated_schema['properties']['is_brittle'])

    def test_verify_schema(self):
        """Test the verification of a schema."""
        unverified_schema = {
            "is_a": "physical_object",
            "properties": {"material": "clay"}
        }
        self.ks.add_schema("clay_pot", unverified_schema, verified=False)
        
        # Verify it's initially unverified
        self.assertFalse(self.ks.get_schema("clay_pot")['verified'])
        
        # Verify the schema
        self.ks.verify_schema("clay_pot")
        
        # Verify it's now verified
        self.assertTrue(self.ks.get_schema("clay_pot")['verified'])

    def test_get_all_schemas(self):
        """Test retrieving all schemas from the store."""
        all_schemas = self.ks.get_all_schemas(include_properties=True)
        self.assertIn('rubber_ball', all_schemas)
        self.assertIn('glass_bottle', all_schemas)
        self.assertIn('tile_floor', all_schemas)
        self.assertTrue(all_schemas['rubber_ball']['properties']['is_brittle'])

if __name__ == '__main__':
    unittest.main() 