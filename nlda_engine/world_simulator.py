"""
The World Simulator: The Engine for Dynamic Reasoning

This component, for v2.0, is a full-fledged physics simulation controller.
It uses pybullet as a backend to model complex, stateful, multi-body
dynamics, representing the pinnacle of the NLDA's grounding capabilities.
"""
import pybullet as p
import time
import math

class WorldSimulator:
    """
    A stateful simulator that uses pybullet to run physics experiments.
    This version is designed to solve the Rotating Platform Paradox.
    """
    def __init__(self, connection_mode=p.DIRECT):
        """Initializes the pybullet physics client."""
        self.client_id = p.connect(connection_mode)
        p.setGravity(0, 0, -9.8, physicsClientId=self.client_id)
        
        # Add a ground plane to stabilize the simulation
        p.createCollisionShape(p.GEOM_PLANE)
        p.createMultiBody(0, p.createCollisionShape(p.GEOM_PLANE))
        
        self.bodies = {} # To store pybullet body IDs
        self.constraints = {} # To store constraint IDs

    def __enter__(self):
        """Enter the context, returning the simulator instance."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context, ensuring disconnection."""
        self.disconnect()

    def setup_platform(self, mass=200, radius=5, initial_omega_z=2):
        """Creates the rotating platform."""
        shape = p.createCollisionShape(p.GEOM_CYLINDER, radius=radius, height=0.1, physicsClientId=self.client_id)
        body = p.createMultiBody(baseMass=mass, baseCollisionShapeIndex=shape, basePosition=[0, 0, 0], physicsClientId=self.client_id)
        p.resetBaseVelocity(body, linearVelocity=[0,0,0], angularVelocity=[0,0,initial_omega_z], physicsClientId=self.client_id)
        self.bodies['platform'] = body
        # Set friction to zero
        p.changeDynamics(body, -1, lateralFriction=0, spinningFriction=0, rollingFriction=0, physicsClientId=self.client_id)

    def add_ball(self, name: str, mass=10, radius=0.2, pos=[0,0,10], vel=[0,0,0], ang_vel=[0,0,0]):
        """Adds a ball to the simulation."""
        shape = p.createCollisionShape(p.GEOM_SPHERE, radius=radius, physicsClientId=self.client_id)
        body = p.createMultiBody(baseMass=mass, baseCollisionShapeIndex=shape, basePosition=pos, physicsClientId=self.client_id)
        p.resetBaseVelocity(body, linearVelocity=vel, angularVelocity=ang_vel, physicsClientId=self.client_id)
        self.bodies[name] = body
    
    def apply_platform_air_resistance(self, beta=0.5):
        """Applies a torque proportional to -ω^2."""
        platform_id = self.bodies['platform']
        _, ang_vel = p.getBaseVelocity(platform_id, physicsClientId=self.client_id)
        omega_z = ang_vel[2]
        torque = -beta * (omega_z**2) * math.copysign(1, omega_z) # Ensure torque opposes motion
        p.applyExternalTorque(platform_id, -1, [0,0,torque], p.WORLD_FRAME, physicsClientId=self.client_id)
        
    def add_wire_constraint(self, ball_name: str, max_force=100):
        """Adds a point-to-point constraint to simulate the wire."""
        ball_id = self.bodies[ball_name]
        platform_id = self.bodies['platform']
        
        # Constrain the ball to a point at the center of the platform
        constraint_id = p.createConstraint(
            parentBodyUniqueId=platform_id,
            parentLinkIndex=-1,
            childBodyUniqueId=ball_id,
            childLinkIndex=-1,
            jointType=p.JOINT_POINT2POINT,
            jointAxis=[0, 0, 0],
            parentFramePosition=[0, 0, 0],
            childFramePosition=[0, 0, 0],
            physicsClientId=self.client_id
        )
        p.changeConstraint(constraint_id, maxForce=max_force, physicsClientId=self.client_id)
        self.constraints[ball_name] = constraint_id

    def remove_wire_constraint(self, ball_name: str):
        """Removes the wire constraint for a given ball."""
        constraint_id = self.constraints.get(ball_name)
        if constraint_id is not None:
            p.removeConstraint(constraint_id, physicsClientId=self.client_id)
            del self.constraints[ball_name]
            print("Wire has been removed.")

    def get_state(self, body_name: str):
        """Gets the position, orientation, linear and angular velocity of a body."""
        body_id = self.bodies[body_name]
        pos, ori = p.getBasePositionAndOrientation(body_id, physicsClientId=self.client_id)
        lin_vel, ang_vel = p.getBaseVelocity(body_id, physicsClientId=self.client_id)
        return {'pos': pos, 'ori': ori, 'lin_vel': lin_vel, 'ang_vel': ang_vel}
        
    def get_contact_points(self, body_a_name, body_b_name):
        """Checks for contact between two bodies."""
        return p.getContactPoints(self.bodies[body_a_name], self.bodies[body_b_name], physicsClientId=self.client_id)

    def step(self):
        """Advances the simulation by one step."""
        p.stepSimulation(physicsClientId=self.client_id)

    def disconnect(self):
        """Disconnects from the physics server."""
        # Check if the client is still connected before trying to disconnect
        if p.isConnected(self.client_id):
            p.disconnect(physicsClientId=self.client_id) 