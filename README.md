# RS2-JENGA

ROS2 workspace for controlling a UR3e robot in Jenga manipulation tasks. Supports simulation (Gazebo) and real hardware, with motion planning via MoveIt2 or RMRC (Resolved Motion Rate Control).

## Package Structure

| Package             | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `ur3e_controller`   | Joint trajectory control, simulation launch files, demo nodes, e-stop      |
| `motion_planning`   | Pose goals, RMRC planner, exclusion zones, MoveIt2 integration             |

## Requirements

- ROS2 Iron or Humble (Ubuntu 22.04)
- For simulation: Gazebo Classic, `ur_description`, `ur_moveit_config`
- For hardware: `ur_robot_driver`, UR3e in external control mode

## Build

```bash
cd ~/ros2_ws
source /opt/ros/iron/setup.bash  # or humble
colcon build --packages-select ur3e_controller motion_planning
source install/setup.bash
```

---

## Start the Environment

Choose **one** option below.

### Option 1: Simulation (Gazebo)

**Using packages in this workspace:**

```bash
# Gazebo sim + RViz
ros2 launch ur3e_controller ur3e_sim_control.launch.py

# Gazebo + MoveIt (planning in RViz)
ros2 launch ur3e_controller ur3e_sim_moveit.launch.py
```

**Or using Universal Robots Gazebo package** (if installed):

```bash
ros2 launch ur_simulation_gazebo ur_sim_moveit.launch.py
```

*Note: The upstream launch may default to UR5e; configure it for UR3e if needed.*

### Option 2: Real Robot

#### 1. Prepare the robot on the tablet

- Press the red button (power off) on the bottom left; if first time, click "confirm configuration".
- Press "On", then "Start" when available.
- Press "Exit".
- Navigate to **Program → Urcaps**.
- Press **External Control** once.

#### 2. Launch driver and RViz

```bash
source /opt/ros/humble/setup.bash
ros2 launch ur_robot_driver ur_control.launch.py ur_type:=ur3e robot_ip:=192.168.56.101 launch_rviz:=true
```

#### 3. Start external control on the tablet

- Press the start/pause button (bottom right, left of "Simulation").
- Press **Play from selection #: Control by Desktop**.

#### 4. Shutdown when finished

- Press the green button (normal mode).
- Press the red "Off" button.
- Power off the tablet; choose "do not save" if prompted.

#### 5. Real robot + MoveIt motion planning

After completing steps 1-3 above (driver running, external control active), open a **second terminal** to launch MoveIt and the motion planning stack together:

```bash
source /opt/ros/iron/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch ur3e_controller ur3e_hw_moveit.launch.py planner:=moveit
```

Available planners: `moveit` (OMPL), `moveit_cartesian` (Cartesian straight-line + OMPL fallback), `rmrc` (RMRC, no MoveIt move_group).

Then send a goal pose:

```bash
ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped \
  "{header: {frame_id: 'base_link'}, pose: {position: {x: 0.3, y: 0.0, z: 0.4}, orientation: {w: 1.0}}}"
```

*Note: On real hardware the driver uses `scaled_joint_trajectory_controller` (respects the teach-pendant speed slider). The `ur3e_hw_moveit.launch.py` launch file handles this override automatically.*

---

## Running Demos

### Joint trajectory demo

After starting the robot (sim or hardware):

```bash
source install/setup.bash
ros2 run ur3e_controller move_ur3e_demo
# or
ros2 run ur3e_controller initials_demo
```

### Motion planning — simulation (pose goals)

1. Start the simulation with MoveIt2 (e.g. `ur3e_sim_moveit.launch.py`).
2. Launch the motion planning stack:

```bash
ros2 launch motion_planning motion_planning.launch.py
```

3. Send a goal pose:

```bash
ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped \
  "{header: {frame_id: 'base_link'}, pose: {position: {x: 0.3, y: 0.0, z: 0.4}, orientation: {w: 1.0}}}"
```

### Motion planning — real robot

See [Option 2 step 5](#5-real-robot--moveit-motion-planning) above.

### RMRC planning (headless simulation, no MoveIt GUI)

```bash
ros2 launch ur3e_controller headless_moveit.launch.py planner:=rmrc
```

Then send goal poses as above, or run:

```bash
ros2 run motion_planning test_rmrc_pose
```

---

## UR3e + OnRobot RG2 (ur_onrobot) and MoveIt Task Constructor (MTC)

Build `jenga_interfaces`, `mtc_pick_place`, `motion_planning`, and the `ur_onrobot_*` packages, source the workspace, and install `moveit_task_constructor` for your distro if not already available.

**Option A — three terminals (manual order)**

1. Driver + mock or hardware:  
   `ros2 launch ur_onrobot_control start_robot.launch.py ur_type:=ur3e onrobot_type:=rg2 use_fake_hardware:=true launch_rviz:=false`
2. MoveIt:  
   `ros2 launch ur_onrobot_moveit_config ur_onrobot_moveit.launch.py ur_type:=ur3e onrobot_type:=rg2 launch_rviz:=true launch_servo:=false`
3. Exclusion zones + e-stop + MTC server:  
   `ros2 launch motion_planning motion_planning.launch.py planner:=mtc mtc_server_mode:=single_pose joint_trajectory_action:=/scaled_joint_trajectory_controller/follow_joint_trajectory publish_world_to_base_tf:=true base_height:=0.0 base_yaw:=0.0`

**Option B — one launch (delayed motion_planning for move_group warm-up)**

`ros2 launch motion_planning ur_onrobot_mtc_bringup.launch.py`

Tweak `use_fake_hardware`, `robot_ip`, `base_height` / `base_yaw` for the real base pose, and `motion_planning_delay_sec` as needed.

**Six-layer Jenga (parametric 18 pick–place steps)** after the stack and action server are up:

`ros2 run motion_planning jenga_tower_mtc_sequencer --ros-args -p pre_wait_sec:=8.0`

Edit [`motion_planning/config/jenga_tower_mtc_layout.yaml`](src/motion_planning/config/jenga_tower_mtc_layout.yaml) for stock and tower frame positions.

To **instantly** place Jenga block collision objects in the assembled tower layout in MoveIt (no robot motion), call `set_jenga_blocks_tower` on `jenga_blocks_scene` (`std_srvs/Trigger`). Use `reset_jenga_blocks` to return them to the stock layout. This only updates the planning scene, not Gazebo or hardware.

---

## Documentation

- [ur3e_controller](src/ur3e_controller/README.md) – joint control, launch files, move client API
- [motion_planning](src/motion_planning/README.md) – pose goals, RMRC, exclusion zones, MoveIt2 integration
