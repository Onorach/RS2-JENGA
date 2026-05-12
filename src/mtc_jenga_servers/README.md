# mtc_jenga_servers

C++ ROS 2 nodes that expose **MoveIt Task Constructor (MTC)** pipelines as **actions** defined in [`jenga_interfaces`](../jenga_interfaces/README.md). Velocity and per-node tuning live in [`config/mtc_velocity_scaling.yaml`](config/mtc_velocity_scaling.yaml).

## Build

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select jenga_interfaces mtc_jenga_servers
source install/setup.bash
```

Requires MoveIt 2, `moveit_task_constructor`, and a running `move_group` with **ExecuteTaskSolutionCapability** so `/execute_task_solution` exists.

## Executables and default action names

Each server reads ROS parameters (including `action_name`); defaults match unqualified names resolved against your namespace.

| Executable | Default action name | `jenga_interfaces` type |
|------------|----------------------|---------------------------|
| `mtc_pick_place_server` | `jenga_pick_place` | `JengaPickPlace` |
| `mtc_arm_ready_server` | `jenga_arm_ready` | `JengaArmReady` |
| `mtc_extract_side_block_server` | `jenga_extract_side_block` | `JengaExtractSideBlock` |
| `mtc_extract_middle_block_server` | `jenga_extract_middle_block` | `JengaExtractMiddleBlock` |
| `mtc_probe_block_server` | `jenga_probe_block` | `JengaProbeBlock` |

Typical SRDF-oriented defaults (override if your MoveIt config differs): `arm_group` = `ur_onrobot_manipulator`, `hand_group` = `ur_onrobot_gripper`, `hand_frame` / `gripper_tcp` = end-effector frame.

## Shared configuration

[`config/mtc_velocity_scaling.yaml`](config/mtc_velocity_scaling.yaml) supplies per-node scaling and related parameters. Launch files and [`motion_planning`](../motion_planning/README.md) often overlay `max_velocity_scaling_factor` and `max_acceleration_scaling_factor`.

## Standalone launches (MoveIt already running)

Use these when `move_group` is up but you do not want the full `motion_planning` stack:

```bash
# Pick/place only (mode: single_pose vs paired_pose for /goal_pose handling)
ros2 launch mtc_jenga_servers mtc_server.launch.py

# Side and/or middle extract servers
ros2 launch mtc_jenga_servers mtc_extract_servers.launch.py which:=both

# Probe server (force-torque guided)
ros2 launch mtc_jenga_servers mtc_probe_server.launch.py
```

## Integrated bringup

For exclusion zones, e-stop, `jenga_blocks_scene`, and **all** MTC servers in one process tree, use:

```bash
ros2 launch motion_planning motion_planning.launch.py planner:=mtc
```

See the [motion_planning README](../motion_planning/README.md) for prerequisites, `mtc_server_mode`, tests, and sequencers.

## See also

- [jenga_interfaces README](../jenga_interfaces/README.md) – action and service definitions
- [motion_planning README](../motion_planning/README.md) – primary MTC operator guide
