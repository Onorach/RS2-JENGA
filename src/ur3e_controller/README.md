# ur3e_controller

ROS2 package to send joint trajectory commands to a UR3e robot. Works with:

- **Simulation**: [Universal_Robots_ROS2_Gazebo_Simulation](https://github.com/UniversalRobots/Universal_Robots_ROS2_Gazebo_Simulation) (Gazebo + `joint_trajectory_controller`)
- **Hardware**: Universal Robots UR3e with [ur_robot_driver](https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver) and `joint_trajectory_controller` active

The same action interface (`/joint_trajectory_controller/follow_joint_trajectory`) is used in both cases.

## Requirements

- ROS2 Humble (Ubuntu 22.04)
- For simulation: `ur_simulation_gazebo` and Gazebo Classic
- For hardware: `ur_robot_driver` and the robot in external control mode

## Build

From your workspace (e.g. `~/ros2_ws`):

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-select ur3e_controller
source install/setup.bash
```

## Usage

### 1. Start the robot (simulation or hardware)

**Simulation (Gazebo + RViz) – from this package only:**

```bash
# Basic Gazebo sim with RViz
ros2 launch ur3e_controller ur3e_sim_control.launch.py

# Gazebo + MoveIt (planning in RViz)
ros2 launch ur3e_controller ur3e_sim_moveit.launch.py
```

**Real robot:**

```bash
ros2 launch ur_robot_driver ur_control.launch.py ur_type:=ur3e robot_ip:=YOUR_ROBOT_IP launch_rviz:=true
# Then put the robot in "External Control" and start the program on the teach pendant.
```

### 2. Run the demo node

In another terminal (after sourcing the workspace):

```bash
source install/setup.bash
ros2 run ur3e_controller move_ur3e_demo
# Or the same demo under the alias:
ros2 run ur3e_controller initials_demo
```

Optional launch file (with custom action name if your controller is namespaced):

```bash
ros2 launch ur3e_controller demo.launch.py
ros2 launch ur3e_controller demo.launch.py action_name:=/my_ns/joint_trajectory_controller/follow_joint_trajectory
```

## Using the client in your own nodes

```python
from ur3e_controller.move_client import UR3eMoveClient, build_trajectory, UR3E_JOINT_NAMES

# Create client (optionally with custom action name)
client = UR3eMoveClient(action_name="/joint_trajectory_controller/follow_joint_trajectory")
client.wait_for_server()

# Single goal position (radians), duration in seconds
client.move_to_positions([0.0, -1.57, 0.0, -1.57, 0.0, 0.0], duration_sec=5.0)

# Multi-point trajectory: list of (time_from_start_sec, [j1..j6])
waypoints = [
    (0.0, [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]),
    (3.0, [0.2, -1.4, 0.2, -1.4, 0.0, 0.2]),
    (6.0, [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]),
]
trajectory = build_trajectory(UR3E_JOINT_NAMES, waypoints, time_from_start_sec=None)
client.send_trajectory(trajectory)
```

Joint order: `shoulder_pan_joint`, `shoulder_lift_joint`, `elbow_joint`, `wrist_1_joint`, `wrist_2_joint`, `wrist_3_joint`.
