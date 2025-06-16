"""
The Ālaya-vijñāna (The Foundational "Knowledge Store")

This module contains the initial "worldview" of the Nalanda Engine.
It defines the schemas for objects and concepts, including their inherent
properties and relationships (their dependent-arising nature).

This version is upgraded to use a NetworkX graph, allowing for a richer
representation of knowledge, per v0.2 of the roadmap.
"""

import networkx as nx

# The raw data for our initial worldview.
INITIAL_SCHEMAS = {
    "glass_bottle": {
        "is_a": "physical_object",
        "name": "glass_bottle",
        "properties": {"material": "glass", "state": "solid", "is_brittle": True, "mass_kg": 0.7}
    },
    "tile_floor": {
        "is_a": "physical_object",
        "name": "tile_floor",
        "properties": {"material": "ceramic", "state": "solid", "is_hard": True}
    },
    "rubber_ball": {
        "is_a": "physical_object",
        "name": "rubber_ball",
        "properties": {"material": "rubber", "state": "solid", "is_brittle": True, "mass_kg": 0.2} # <-- FLAWED BELIEF
    }
}

class KnowledgeStore:
    """
    A graph-based representation of the AI's beliefs about the world.
    """
    def __init__(self, initial_schemas=None):
        if initial_schemas is None:
            initial_schemas = INITIAL_SCHEMAS
        
        self.graph = nx.DiGraph()
        self._load_schemas(initial_schemas)

    def add_schema(self, name: str, data: dict, verified: bool = True):
        """
        Adds a single schema to the graph, marking it as verified or not.
        """
        # Add the node with all its data.
        self.graph.add_node(name, **data)
        # Explicitly set the verification status.
        self.graph.nodes[name]['verified'] = verified
        
        # Add relationship edges.
        if 'is_a' in data:
            # Ensure the parent node exists, otherwise add a placeholder
            if not self.graph.has_node(data['is_a']):
                self.graph.add_node(data['is_a'], verified=True) # Assume parent concepts are verified
            self.graph.add_edge(name, data['is_a'])
        print(f"[KnowledgeStore] Added schema '{name}' (Verified: {verified})")

    def _load_schemas(self, schemas):
        """Populates the graph from a dictionary of schemas."""
        for name, data in schemas.items():
            # Initial schemas from our code are considered verified by default.
            self.add_schema(name, data, verified=True)

    def get_schema(self, schema_name: str) -> dict:
        """Retrieves all data for a given schema/node."""
        if self.graph.has_node(schema_name):
            return self.graph.nodes[schema_name]
        return None

    def update_property(self, schema_name: str, property_key: str, property_value):
        """Updates a specific property within a schema's properties dictionary."""
        if self.graph.has_node(schema_name):
            self.graph.nodes[schema_name]['properties'][property_key] = property_value

    def verify_schema(self, schema_name: str):
        """
        Promotes an unverified schema to a verified one.
        """
        if self.graph.has_node(schema_name):
            self.graph.nodes[schema_name]['verified'] = True
            print(f"[KnowledgeStore] Schema '{schema_name}' has been verified.")

    def get_all_schemas(self, include_properties=False):
        """
        Returns a dictionary of all schemas in the store.
        """
        schemas = {}
        for node, data in self.graph.nodes(data=True):
            if include_properties:
                schemas[node] = data
            else:
                # Exclude bulky properties for a cleaner view
                schemas[node] = {k: v for k, v in data.items() if k != 'properties'}
        return schemas 