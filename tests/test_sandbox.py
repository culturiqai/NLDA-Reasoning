import unittest
import sys
import os

# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlda_engine.sandbox import Sandbox

class TestSandbox(unittest.TestCase):
    """Unit tests for the Sandbox class."""

    def setUp(self):
        """Set up a new Sandbox for each test."""
        self.sandbox = Sandbox()

    def tearDown(self):
        """Clean up the sandbox after each test."""
        del self.sandbox

    def test_rubber_ball_bounces(self):
        """Test that a rubber ball correctly bounces."""
        rubber_ball_schema = {
            'name': 'rubber_ball',
            'properties': {'mass_kg': 0.5, 'material': 'rubber'}
        }
        result = self.sandbox.get_ground_truth(rubber_ball_schema)
        self.assertEqual(result, "The rubber_ball will bounce.")

    def test_glass_ball_shatters(self):
        """Test that a glass ball correctly shatters."""
        glass_ball_schema = {
            'name': 'glass_ball',
            'properties': {'mass_kg': 0.8, 'material': 'glass'}
        }
        result = self.sandbox.get_ground_truth(glass_ball_schema)
        self.assertEqual(result, "The glass_ball will shatter.")

    def test_porcelain_doll_shatters(self):
        """Test that a porcelain doll correctly shatters."""
        porcelain_doll_schema = {
            'name': 'porcelain_doll',
            'properties': {'mass_kg': 1.2, 'material': 'porcelain'}
        }
        result = self.sandbox.get_ground_truth(porcelain_doll_schema)
        self.assertEqual(result, "The porcelain_doll will shatter.")
        
    def test_generic_object_bounces(self):
        """Test that a generic, non-brittle object bounces by default."""
        generic_object_schema = {
            'name': 'generic_object',
            'properties': {'mass_kg': 1.0, 'material': 'wood'}
        }
        result = self.sandbox.get_ground_truth(generic_object_schema)
        self.assertEqual(result, "The generic_object will bounce.")

if __name__ == '__main__':
    unittest.main() 