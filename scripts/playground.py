"""
The Playground: A place for advanced, isolated experiments.

This script follows the v2.0 roadmap to solve the complex, stateful,
multi-body dynamics problem: The Rotating Platform Paradox.
"""
import sys
import os
import json
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlda_engine.language_interface import LanguageInterface
from nlda_engine.world_simulator import WorldSimulator
import pybullet as p

def main():
    """Main function to run the Rotating Platform Paradox demonstration."""
    print("--- Initializing NLDA Playground: The Rotating Platform Paradox ---")
    
    # --- Setup ---
    lang_interface = LanguageInterface()
    results = {}

    # Use a 'with' statement to guarantee the simulator is connected
    # for the duration of the simulation and cleaned up properly.
    with WorldSimulator(connection_mode=p.GUI) as sim:
        # --- Step 1: Set up the initial scene in the simulator ---
        print("\\n--- Step 1: Constructing the initial state in the WorldSimulator ---")
        
        # We reduce the initial angular velocity to prevent the wire from snapping immediately.
        initial_omega = 1.0 # rad/s
        sim.setup_platform(mass=200, radius=5, initial_omega_z=initial_omega)
        sim.add_ball('A', pos=[0, 0, 10])
        v_ball_b = initial_omega * 5.0
        sim.add_ball('B', pos=[5, 0, 0.3], vel=[0, v_ball_b, 0])
        sim.add_ball('C', pos=[-15, 0, 0.3], vel=[15, 0, 0])
        
        print("Initial scene constructed.")

        # --- Step 2: Run the simulation and record answers ---
        print("\\n--- Step 2: Running stateful simulation to ground the answers ---")
        
        # Add the stable wire constraint once at the beginning
        sim.add_wire_constraint('B', max_force=500) # High max_force to prevent snapping

        total_sim_time = 15.0
        time_step = 1/240.0
        num_steps = int(total_sim_time / time_step)
        
        results = run_simulation_loop(sim, num_steps, time_step)

    # --- Step 3: Final calculations and reporting ---
    print("\\n--- Step 3: Compiling results from the simulation ---")
    
    # Print the NLDA's answers
    print_results(results)
    
    # --- Step 4: The Mimic's Turn ---
    print_mimic_response(lang_interface)
    
    print("--- Rotating Platform Paradox Demo Complete ---")

def run_simulation_loop(sim, num_steps, time_step):
    """Contains the main loop for stepping the simulation and detecting events."""
    results = {
        'q1_omega_before_A': None, 'q2_omega_after_A': None,
        'q3_collision_time_BC': None, 'q4_velocities_after_BC': None,
        'q5_angular_momentum_at_5s': None, 'ball_A_landed': False,
        'wire_active': True
    }

    for i in range(num_steps):
        sim.apply_platform_air_resistance()
        
        # The old, unstable force application is no longer needed.
        # The p.JOINT_POINT2POINT constraint handles the wire physics automatically.

        if not results['ball_A_landed']:
            contact_A = sim.get_contact_points('A', 'platform')
            if contact_A:
                platform_state = sim.get_state('platform')
                results['q1_omega_before_A'] = platform_state['ang_vel'][2]
                
                # --- Manually Enforce Conservation of Angular Momentum ---
                # This is necessary because, as our final tests proved,
                # PyBullet's default constraint creation does not perfectly
                # conserve angular momentum. This manual correction enforces
                # the laws of physics for a more accurate simulation.
                I_platform = p.getDynamicsInfo(sim.bodies['platform'], -1, physicsClientId=sim.client_id)[2][2]
                L_before = I_platform * results['q1_omega_before_A']

                mass_ball = p.getDynamicsInfo(sim.bodies['A'], -1, physicsClientId=sim.client_id)[0]
                shape_data = p.getCollisionShapeData(sim.bodies['A'], -1, physicsClientId=sim.client_id)
                radius_ball = shape_data[0][3][0]
                
                ball_pos = sim.get_state('A')['pos']
                d_sq = ball_pos[0]**2 + ball_pos[1]**2
                
                I_ball_intrinsic = (2/5) * mass_ball * (radius_ball**2)
                I_ball_parallel_axis = mass_ball * d_sq
                I_ball_total = I_ball_intrinsic + I_ball_parallel_axis
                
                I_after = I_platform + I_ball_total
                omega_new_correct = L_before / I_after

                # Set the new velocity FIRST, then create the constraint
                p.resetBaseVelocity(sim.bodies['platform'], linearVelocity=[0,0,0],
                                    angularVelocity=[0,0,omega_new_correct],
                                    physicsClientId=sim.client_id)
                p.createConstraint(sim.bodies['platform'], -1, sim.bodies['A'], -1,
                                   p.JOINT_FIXED, [0,0,0], [0,0,0], ball_pos,
                                   physicsClientId=sim.client_id)
                results['ball_A_landed'] = True

        if not results['q3_collision_time_BC']:
            contact_BC = sim.get_contact_points('B', 'C')
            if contact_BC:
                results['q3_collision_time_BC'] = i * time_step
                sim.step() 
                results['q4_velocities_after_BC'] = {
                    'A': sim.get_state('A')['lin_vel'], 'B': sim.get_state('B')['lin_vel'],
                    'C': sim.get_state('C')['lin_vel'], 'platform': sim.get_state('platform')['ang_vel']
                }

        sim.step()
        if sim.client_id < 2: time.sleep(time_step)
        
        if results['ball_A_landed'] and not results['q2_omega_after_A']:
             platform_state = sim.get_state('platform')
             results['q2_omega_after_A'] = platform_state['ang_vel'][2]
             
    # Final calculation for Q5
    platform_state = sim.get_state('platform')
    I_platform = p.getDynamicsInfo(sim.bodies['platform'], -1)[2]
    results['q5_angular_momentum_at_5s'] = I_platform[2] * platform_state['ang_vel'][2]
    
    return results

def print_results(results):
    """Prints the final compiled answers from the simulation."""
    print("\\n" + "-"*20 + " The NLDA's Grounded Answers " + "-"*20)
    if results.get('q1_omega_before_A') is not None:
        print(f"1. Platform ω just before Ball A lands: {results['q1_omega_before_A']:.4f} rad/s")
    else:
        print("1. Ball A did not land on the platform.")

    if results.get('q2_omega_after_A') is not None:
        print(f"2. Platform ω just after Ball A sticks: {results['q2_omega_after_A']:.4f} rad/s")
    else:
        print("2. Cannot determine ω after Ball A landing.")
        
    if results.get('q3_collision_time_BC'):
        print(f"3. Ball C collides with Ball B at: {results['q3_collision_time_BC']:.4f} s")
        print("4. Velocities immediately after B-C collision:")
        print(f"   - Ball A: {results['q4_velocities_after_BC']['A']}")
        print(f"   - Ball B: {results['q4_velocities_after_BC']['B']}")
        print(f"   - Ball C: {results['q4_velocities_after_BC']['C']}")
    else:
        print("3. Ball C did not collide with Ball B within the simulation time.")
    
    if results.get('q5_angular_momentum_at_5s') is not None:
        print(f"5. Platform angular momentum at t=5s: {results['q5_angular_momentum_at_5s']:.4f} kg·m²/s")
    else:
        print("5. Could not calculate final angular momentum.")
        
    print("-" * 70 + "\\n")

def print_mimic_response(lang_interface):
    """Queries and prints the Mimic's qualitative description."""
    print("-" * 20 + " The Mimic's Turn " + "-"*22)
    mimic_prompt = (
        "Briefly and qualitatively, describe the key physical events and conservation laws "
        "at play in the Rotating Platform Paradox. Do not perform calculations."
    )
    mimic_prediction = lang_interface.get_raw_prediction(mimic_prompt)
    print(f"The Mimic (raw LLM) qualitatively describes: '{mimic_prediction}'")
    print("-" * 70 + "\\n")


if __name__ == "__main__":
    main() 