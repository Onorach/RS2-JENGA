import numpy as np
import pytest
from motion_planning.rmrc_planner import RMRCPlanner, Obstacle, SOLID_PRIMITIVE_BOX
from motion_planning.kinematics_backends import Pose, PyKDLKinematicsBackend

# --- MOCK DATA ---
def get_planner():
    # Initialize your planner with a real backend (PyKDL) 
    # to ensure the Jacobian math is actually tested.
    backend = PyKDLKinematicsBackend(
        urdf_path="/path/to/your/ur3e.urdf", # Update this path!
        base_link="base_link",
        ee_link="tool0"
    )
    return RMRCPlanner(backend=backend)

# --- THE TESTS ---

def test_ground_plane_repulsion():
    planner = get_planner()
    # Create a ground plane obstacle at z = -0.05
    ground = Obstacle(
        name="ground", 
        type=SOLID_PRIMITIVE_BOX, 
        dimensions=[2.0, 2.0, 0.01], 
        pose=Pose(position=np.array([0, 0, -0.05]), quaternion=np.array([0,0,0,1]))
    )
    
    # Pose where the elbow is very low (Shoulder lift = -1.8 rad)
    q_low = np.array([0.0, -1.8, 2.0, 0.0, 0.0, 0.0]) 
    
    # Verify the repulsion logic
    # In your code, this usually returns a joint velocity vector (dq)
    dq_repulsion = planner._compute_repulsion(q_low, [ground])
    
    # If the arm is near the ground, the velocity for the lift joint 
    # should be positive (moving UP)
    assert dq_repulsion[1] > 0, f"Expected positive dq[1] to move away from floor, got {dq_repulsion[1]}"

def test_dls_matrix_inversion():
    planner = get_planner()
    # A fully extended arm is singular
    q_singular = np.zeros(6) 
    J = planner.backend.compute_jacobian(q_singular)
    
    # Task: move 1m/s in X (impossible at extension)
    v_task = np.array([1.0, 0, 0, 0, 0, 0])
    
    # Use your planner's internal solver (which uses DLS)
    # This checks if the damping lambda is high enough to prevent NaNs or infinite speed
    q_dot = planner._solve_rmrc(J, v_task, damping=0.01)
    
    assert not np.isnan(q_dot).any(), "DLS returned NaN"
    assert np.all(np.abs(q_dot) < 10.0), f"Velocities too high at singularity: {q_dot}"

def test_ik_continuity():
    # This tests the "Elbow Swing" issue
    planner = get_planner()
    current_q = np.array([0.0, -1.57, 1.57, 0, 0, 0]) # Elbow Up
    
    # Goal that is reachable in multiple configs
    goal_pose = Pose(position=np.array([0.3, 0.1, 0.3]), quaternion=np.array([0, 0, 0, 1]))
    
    # Check your IK selection logic
    # We want to ensure it picks a solution close to 'current_q' 
    # and doesn't flip the elbow sign.
    best_q = planner._solve_ik_closest(goal_pose, current_q)
    
    # Check if the elbow joint (index 2) flipped direction
    assert np.sign(best_q[2]) == np.sign(current_q[2]), "IK solver flipped the elbow configuration!"