# rs2_jenga

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
colcon build --packages-select rs2_jenga
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
ros2 run rs2_jenga move_ur3e_demo
# Or the same demo under the alias:
ros2 run rs2_jenga initials_demo
```

Optional launch file (with custom action name if your controller is namespaced):

```bash
ros2 launch rs2_jenga demo.launch.py
ros2 launch rs2_jenga demo.launch.py action_name:=/my_ns/joint_trajectory_controller/follow_joint_trajectory
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

---

## Motion planning and control (MoveIt2)

This package can plan **collision-free Cartesian motions** and handle **inverse kinematics** via MoveIt2, then execute on the same joint trajectory controller (sim or hardware).

### Pose goals and trajectory planning

1. Start the robot and **MoveIt2** (e.g. `ur3e_sim_moveit.launch.py` or `ur_moveit_config` with real robot).
2. Start the motion planning stack:

```bash
ros2 launch ur3e_controller motion_planning.launch.py
```

3. Send a goal pose (frame_id must match your planning frame, e.g. `base_link`):

```bash
ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped "{header: {frame_id: 'base_link'}, pose: {position: {x: 0.3, y: 0.0, z: 0.4}, orientation: {w: 1.0}}}"
```

The node will plan a collision-free path to that pose and execute it. Alternatively, set a pose on `/goal_pose` and call the service to execute:

```bash
ros2 service call /execute_last_goal_pose std_srvs/srv/Trigger
```

**Parameters:**

- `plan_only` (default: false): if true, only plans and does not execute.
- `move_action_name` (default: `/move_action`): MoveGroup action name from MoveIt2.

### Exclusion zones (no-go regions)

To keep the robot (or any part of it) out of certain regions (sim or hardware), add **exclusion zones** as collision objects to the planning scene. MoveIt2 will then plan around them.

- **From YAML at startup:** copy `config/exclusion_zones_example.yaml`, edit boxes/spheres (frame, position, size/radius), then:

```bash
ros2 launch ur3e_controller motion_planning.launch.py exclusion_zones_file:=/path/to/your/exclusion_zones.yaml
```

- **From code:** use `MoveItPlanningInterface.add_exclusion_zone_box()` and `add_exclusion_zone_sphere()`, or the helper in `exclusion_zones_loader.py` (`apply_exclusion_zones_to_scene()`).

Standalone loader node (e.g. if you don’t use `motion_planning.launch.py`):

```bash
ros2 run ur3e_controller exclusion_zones_node --ros-args -p exclusion_zones_file:=/path/to/zones.yaml
```

### Force/torque feedback

When the UR3e (or sim) exposes force/torque at the tool (e.g. via `force_torque_sensor_broadcaster` with `topic_name: ft_data`), the **pose goal node** subscribes to that topic and caches the latest wrench. You can use it for monitoring or compliance:

- **Topic:** default `/ft_data` (configurable via `ft_topic` parameter on the pose goal node).
- **Message type:** `geometry_msgs/WrenchStamped`.
- In code, the node’s `get_latest_wrench()` returns the latest reading (or use the topic directly from other nodes).
