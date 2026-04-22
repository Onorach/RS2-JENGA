import numpy as np
from motion_planning.rmrc_planner import RMRCPlanner, Obstacle

def test_repulsion():
    # 1. Setup a dummy planner and a single obstacle
    planner = RMRCPlanner(...) 
    obs = Obstacle(name="test_box", type=1, dimensions=[0.2, 0.2, 0.2], pose=...)
    
    # 2. Manually call the repulsion logic
    # See if the resulting joint velocities push the arm AWAY from the obstacle
    q_test = np.array([0, -1.57, 1.57, 0, 0, 0])
    repulsion_v = planner._compute_repulsion(q_test, [obs])
    print(f"Repulsion Vector: {repulsion_v}")

def test_dls_inversion():
    # 1. Create a singular Jacobian
    J = np.zeros((6, 6)) # Or use planner.backend.compute_jacobian
    # 2. Attempt to invert with DLS damping
    # 3. Verify it doesn't return NaNs or Inf
    pass

if __name__ == "__main__":
    test_repulsion()