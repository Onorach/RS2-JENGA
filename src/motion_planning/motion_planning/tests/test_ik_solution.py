import numpy as np
import pytest
from motion_planning.rmrc_planner import RMRCPlanner, Obstacle

def test_ground_plane_repulsion():
    # Setup a planner with a ground plane obstacle
    planner = RMRCPlanner(...) 
    ground = Obstacle(
        name="ground", type=1, 
        dimensions=[2.0, 2.0, 0.01], 
        pose=Pose(position=np.array([0, 0, -0.01]), quaternion=np.array([0,0,0,1]))
    )
    
    # Configuration where the elbow is dangerously low
    # (Shoulder lift down, Elbow extended)
    q_low = np.array([0.0, -1.8, 2.0, 0.0, 0.0, 0.0]) 
    
    # Calculate repulsion
    repulsion_dq = planner._compute_repulsion(q_low, [ground])
    
    # VERIFICATION: The velocity for joint 1 (shoulder_lift) or 2 (elbow) 
    # should be POSITIVE to move the arm AWAY from the ground.
    assert repulsion_dq[1] > 0 or repulsion_dq[2] < 0, \
        f"Repulsion failed to push arm up. dq: {repulsion_dq}"

def test_dls_stability():
    planner = RMRCPlanner(...)
    # Create a singular Jacobian (arm fully extended)
    q_singular = np.array([0, 0, 0, 0, 0, 0])
    J = planner.backend.compute_jacobian(q_singular)
    
    # Try to move in an "impossible" direction (e.g., pulling the arm longer)
    v_task = np.array([1.0, 0, 0, 0, 0, 0]) 
    
    # Run the inversion logic (manual check of your _solve_rmrc or similar)
    # If the resulting q_dot has components > 10.0 rad/s, your damping is too low.
    q_dot = planner._calculate_velocities(q_singular, v_task)
    
    assert np.all(np.abs(q_dot) < 5.0), "DLS failing to bound velocities at singularity"

def test_ik_consistency():
    backend = URAnalyticalIKBackend()
    target_pose = Pose(...) # Your problematic goal
    current_q = np.array([0, -1.57, 1.57, 0, 0, 0]) # Elbow UP start
    
    # Get all IK solutions
    solutions = backend.compute_ik(target_pose)
    
    # Check if the "best" solution according to your planner logic 
    # is actually the one closest to current_q
    # If it picks a solution where q[2] (elbow) flips sign, that's your swing.
    best_q = planner._select_best_ik(solutions, current_q)
    
    elbow_flip = np.sign(current_q[2]) != np.sign(best_q[2])
    assert not elbow_flip, "Planner selected an IK solution that flips the elbow!"