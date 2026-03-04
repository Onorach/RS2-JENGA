# ur3e_controller

ROS2 Humble node that sends movement commands to a UR3e (or other UR e-series) via a **single interface**: subscribe to Cartesian goal poses, and the node uses MoveIt to plan and execute on either **simulation** (Gazebo + RViz) or **hardware**.

## Interface

- **Input**: `geometry_msgs/msg/PoseStamped` on topic **`/move_group/goal`**
  - Frame and pose in that frame (e.g. `base_link`). MoveIt plans to reach that pose with the end effector.
- **Output**: `std_msgs/msg/Int32` on topic **`/ur_status`**
  - `0` = Ready, `1` = Executing, `2` = Done, `3` = Planning failed, `4` = Execution failed.

The same node and topic interface is used for both simulation and real robot; only the launch stack (sim vs hardware) changes.

## Simulation (Gazebo + RViz + MoveIt)

Uses [Universal_Robots_ROS2_Gazebo_Simulation](https://github.com/UniversalRobots/Universal_Robots_ROS2_Gazebo_Simulation): Gazebo for physics, RViz and MoveIt for planning and visualisation. Trajectories are executed by `joint_trajectory_controller` on the simulated robot.

**Prerequisites**: Install and build the simulation package (e.g. from the same workspace or via the `.repos` in that repo).

**Launch everything (Gazebo, MoveIt, RViz, and this controller):**

```bash
ros2 launch ur3e_controller ur3e_sim.launch.py
```

Optional arguments:

- `ur_type:=ur3e` (default) or other type supported by the simulation (e.g. `ur5e`)
- `velocity_scaling:=0.5` (default, range 0.01–1.0)
- `planning_group:=ur_manipulator` (default)

**Send a goal (example):**

```bash
ros2 topic pub --once /move_group/goal geometry_msgs/msg/PoseStamped \
  "{ header: { frame_id: 'base_link' }, pose: { position: { x: 0.3, y: 0.2, z: 0.4 }, orientation: { x: 0.0, y: 0.707, z: 0.0, w: 0.707 } } }"
```

## Hardware (real UR3e)

MoveIt and the official Universal Robots ROS2 driver must be running so that trajectories are executed on the real robot (e.g. via `scaled_joint_trajectory_controller`). This package only runs the **ur3e_controller** node that subscribes to `/move_group/goal` and uses MoveIt to plan and execute.

**Prerequisites**: Install and run the [Universal_Robots_ROS2_Driver](https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver) and MoveIt (e.g. `ur_bringup`, `ur_moveit_config`).

**1. Start the robot driver** (replace `YOUR_ROBOT_IP` and adjust `ur_type` if needed):

```bash
ros2 launch ur_bringup ur_control.launch.py ur_type:=ur3e robot_ip:=YOUR_ROBOT_IP
```

**2. Start MoveIt** (with real hardware, **not** fake):

```bash
ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur3e use_fake_hardware:=false
```

**3. Start this controller node:**

```bash
ros2 launch ur3e_controller ur3e_hardware.launch.py
```

Optional arguments: `velocity_scaling:=0.5`, `planning_group:=ur_manipulator`.

**Send a goal**: same as in simulation, by publishing a `PoseStamped` to `/move_group/goal`.

## Summary

| Use case   | Launch file              | Prerequisites                                      |
|-----------|---------------------------|----------------------------------------------------|
| Simulation| `ur3e_sim.launch.py`     | `ur_simulation_gazebo` (Gazebo + MoveIt + RViz)   |
| Hardware  | `ur3e_hardware.launch.py`| `ur_bringup` + `ur_moveit_config` (driver + MoveIt)|

The same movement interface (`/move_group/goal` → plan & execute) is used in both cases.
