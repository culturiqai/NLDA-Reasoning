"""
The Sandbox: Ground Truth Reality

This module simulates the real world, providing the "ground truth" outcome
for any given event, against which the AGI can compare its predictions.
This is upgraded for v0.3 to use the PyBullet physics engine.
"""
import pybullet as p
import time

class Sandbox:
    """
    A physics-based sandbox to determine ground truth for events.
    """
    def __init__(self):
        try:
            # Connect to PyBullet in direct mode (no GUI)
            self.physics_client = p.connect(p.DIRECT)
        except p.error:
            print("Warning: PyBullet could not be initialized. Sandbox will use simplified logic.")
            self.physics_client = None

    def get_ground_truth(self, object_schema: dict) -> str:
        """
        Determines the real outcome based on true physics.
        If PyBullet is available, it runs a simulation.
        Otherwise, it falls back to simple rule-based logic.
        """
        if self.physics_client is not None:
            return self._get_pybullet_ground_truth(object_schema)
        else:
            return self._get_simplified_ground_truth(object_schema)

    def _get_simplified_ground_truth(self, object_schema: dict) -> str:
        """Fallback logic if PyBullet fails."""
        # This logic is based on the object's *actual* properties, not the engine's belief
        name = object_schema.get('name', 'object')
        if name == 'rubber_ball': # The ground truth is that rubber balls are not brittle
            return f"The {name} will bounce."
        elif object_schema.get('properties', {}).get('is_brittle', False):
             return f"The {name} will shatter."
        else:
            return f"The {name} will bounce."

    def _get_pybullet_ground_truth(self, object_schema: dict) -> str:
        """
        Runs a full physics simulation to determine the outcome.
        """
        p.resetSimulation(physicsClientId=self.physics_client)
        p.setGravity(0, 0, -9.8, physicsClientId=self.physics_client)

        # Create the floor
        p.createCollisionShape(p.GEOM_PLANE, physicsClientId=self.physics_client)
        p.createMultiBody(0, 0, physicsClientId=self.physics_client)

        # Get object properties for the simulation
        name = object_schema.get('name', 'object')
        properties = object_schema.get('properties', {})
        mass_kg = properties.get('mass_kg', 1.0)
        
        # Ground truth brittleness (different from engine's belief)
        brittle_materials = ["glass", "porcelain", "ceramic"]
        is_actually_brittle = any(mat in name for mat in brittle_materials)

        # A more robust check could use the material property if available
        material = properties.get('material', '').lower()
        if material in brittle_materials:
            is_actually_brittle = True
        
        # Create the object
        start_pos = [0, 0, 2] # Drop from 2 meters
        col_shape_id = p.createCollisionShape(p.GEOM_SPHERE, radius=0.1, physicsClientId=self.physics_client)
        body_id = p.createMultiBody(baseMass=mass_kg, baseCollisionShapeIndex=col_shape_id, basePosition=start_pos, physicsClientId=self.physics_client)

        # Run the simulation
        for _ in range(240 * 2): # Simulate for 2 seconds
            p.stepSimulation(physicsClientId=self.physics_client)
        
        # Check for collision and velocity after impact
        contact_points = p.getContactPoints(bodyA=body_id, physicsClientId=self.physics_client)
        post_impact_velocity = p.getBaseVelocity(body_id, physicsClientId=self.physics_client)[0][2]

        shatter_force_threshold = 5.0 # A proxy for brittleness in the simulation
        
        # Simplified outcome logic
        outcome = f"The {name} will bounce." # Default outcome
        if contact_points:
            # Calculate an estimated impact force (very simplified)
            impact_force = mass_kg * 9.8 * 2 
            if is_actually_brittle and impact_force > shatter_force_threshold:
                outcome = f"The {name} will shatter."
            elif post_impact_velocity > 0.01: # Check if it's bouncing up
                outcome = f"The {name} will bounce."
        
        return outcome

    def get_tool_use_ground_truth(self, tool_schema: dict, target_schema: dict) -> str:
        """
        Determines the real outcome for a tool striking a target.
        For now, this uses simplified rule-based logic. A full implementation
        would involve a more complex PyBullet simulation.
        """
        tool_name = tool_schema.get('name', 'tool')
        target_name = target_schema.get('name', 'target')

        # Use the same "actual brittleness" logic from the drop test
        brittle_materials = ["glass", "porcelain", "ceramic"]
        target_material = target_schema.get('properties', {}).get('material', '').lower()
        is_target_actually_brittle = target_material in brittle_materials

        # A simplified assumption for the demo
        is_tool_actually_hard = "plastic" in tool_schema.get('properties', {}).get('material', '').lower()

        print(f"[SANDBOX-TOOL] Simulating strike: '{tool_name}' (hard: {is_tool_actually_hard}) -> '{target_name}' (brittle: {is_target_actually_brittle}).")

        if is_tool_actually_hard and is_target_actually_brittle:
            return f"The {target_name} will shatter when struck by the {tool_name}."
        else:
            return f"The {target_name} will be dented or bounce off the {tool_name}."

    def __del__(self):
        if self.physics_client is not None:
            try:
                p.disconnect(physicsClientId=self.physics_client)
            except p.error:
                pass # Already disconnected or failed to init

if __name__ == '__main__':
    # Example usage
    sandbox = Sandbox()
    
    # --- Test Case 1: Rubber Ball (Engine believes it's brittle) ---
    rubber_ball_schema = {
        'name': 'rubber_ball',
        'properties': {'mass_kg': 0.5, 'is_brittle': True} # Engine's flawed belief
    }
    # But the sandbox knows the ground truth
    truth1 = sandbox.get_ground_truth(rubber_ball_schema)
    print(f"Testing with: {rubber_ball_schema['name']}")
    print(f" -> Ground Truth: {truth1}\n") # Expected: will bounce

    # --- Test Case 2: Glass Ball (Engine believes it's brittle) ---
    glass_ball_schema = {
        'name': 'glass_ball',
        'properties': {'mass_kg': 0.8, 'is_brittle': True, 'material': 'glass'} # Engine's correct belief
    }
    truth2 = sandbox.get_ground_truth(glass_ball_schema)
    print(f"Testing with: {glass_ball_schema['name']}")
    print(f" -> Ground Truth: {truth2}\n") # Expected: will shatter
    
    # --- Test Case 3: Porcelain Doll ---
    porcelain_doll_schema = {
        'name': 'porcelain_doll',
        'properties': {'mass_kg': 1.2, 'is_brittle': True, 'material': 'porcelain'}
    }
    truth3 = sandbox.get_ground_truth(porcelain_doll_schema)
    print(f"Testing with: {porcelain_doll_schema['name']}")
    print(f" -> Ground Truth: {truth3}\n") # Expected: will shatter
    
    del sandbox 