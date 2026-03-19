# motion_planning

ROS2 package for motion planning with a UR3e: pose goals, RMRC (Resolved Motion Rate Control), exclusion zones, and MoveIt2 integration. Executes planned trajectories via the `ur3e_controller` move client.

## Features

- **Pose goal node** – Cartesian pose goals via MoveIt2 (IK + planning + execution)
- **RMRC planner** – Jacobian-based Cartesian planning with potential-field collision avoidance (no MoveIt GUI)
- **Exclusion zones** – No-go regions (boxes, spheres) loaded from YAML or added in code
- **E-stop integration** – Works with `ur3e_controller` estop node to cancel trajectories

## Requirements

- ROS2 Humble or Iron
- `ur3e_controller` (for trajectory execution)
- `ur_moveit_config` (when using MoveIt pose goal node)
- `ur_description` (for RMRC)
- Python: `numpy`, `ikpy`, `yaml`

## Build

```bash
source /opt/ros/humble/setup.bash  # or iron
colcon build --packages-select motion_planning
source install/setup.bash
```

## Nodes

| Node                   | Description                                                              |
|------------------------|--------------------------------------------------------------------------|
| `pose_goal_node`       | MoveIt2 pose goals; plans and executes via `/move_action`               |
| `rmrc_planning_node`   | RMRC Cartesian planner; no MoveIt; uses Jacobian + repulsion           |
| `exclusion_zones_node` | Loads exclusion zones from YAML into the MoveIt planning scene         |
| `test_rmrc_pose`       | Test script that publishes sample goal poses                            |
| `robot_gui`            | GUI for robot interaction                                               |

## Launch

### Main launch file

Start this **after** the robot and (optionally) MoveIt2 are running:

```bash
ros2 launch motion_planning motion_planning.launch.py
```

**Parameters:**

| Parameter                 | Default                            | Description                                          |
|---------------------------|------------------------------------|------------------------------------------------------|
| `use_rmrc`                | `false`                            | Use RMRC instead of MoveIt pose_goal_node           |
| `exclusion_zones_file`    | `config/ur3e_workspace.yaml`       | Path to YAML defining exclusion zones               |
| `plan_only`               | `false`                            | Plan only, do not execute                            |
| `add_floor_plane`         | `true`                             | Add floor-plane collision object                     |
| `floor_z`                  | `0.0`                              | Floor Z height (metres)                              |

**Examples:**

```bash
# With custom exclusion zones
ros2 launch motion_planning motion_planning.launch.py exclusion_zones_file:=/path/to/zones.yaml

# RMRC planning (no MoveIt GUI)
ros2 launch motion_planning motion_planning.launch.py use_rmrc:=true
```

### Standalone exclusion zones loader

If you run pose/RMRC planning separately:

```bash
ros2 run motion_planning exclusion_zones_node --ros-args -p exclusion_zones_file:=/path/to/zones.yaml
```

## Sending goal poses

**Topic:** `/goal_pose` (`geometry_msgs/PoseStamped`)

```bash
ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped \
  "{header: {frame_id: 'base_link'}, pose: {position: {x: 0.3, y: 0.0, z: 0.4}, orientation: {w: 1.0}}}"
```

**Service:** `/execute_last_goal_pose` (`std_srvs/Trigger`) – execute the last pose set on `/goal_pose`.

## Exclusion zones

Exclusion zones are collision objects (boxes or spheres) added to the MoveIt planning scene so the robot plans around them.

### YAML schema

```yaml
exclusion_zones:
  - type: box
    id: cabinet_body
    frame_id: base_link
    position: [x, y, z]
    size: [x, y, z]

  - type: sphere
    id: tower_zone
    frame_id: base_link
    center: [x, y, z]
    radius: 0.1
```

### Runtime control

```bash
ros2 topic pub --once /remove_exclusion_zone std_msgs/msg/String "data: cabinet_body"
ros2 topic pub --once /add_exclusion_zone    std_msgs/msg/String "data: cabinet_body"
```

### Use from code

```python
from motion_planning.moveit_planning import MoveItPlanningInterface
# add_exclusion_zone_box(), add_exclusion_zone_sphere()

from motion_planning.exclusion_zones_loader import apply_exclusion_zones_to_scene
# apply_exclusion_zones_to_scene(scene, zones_from_yaml)
```

## RMRC vs MoveIt

| Aspect        | MoveIt (`use_rmrc:=false`)      | RMRC (`use_rmrc:=true`)        |
|---------------|----------------------------------|---------------------------------|
| GUI           | RViz + MoveIt                   | Optional; can run headless      |
| Planning      | OMPL                            | Jacobian + potential field      |
| Dependencies  | MoveIt2, move_group              | `ur_description` only           |
| Use case      | Full planning pipeline          | Fast Cartesian, no MoveIt stack  |

## See also

- [ur3e_controller](../ur3e_controller/README.md) – joint control, sim launch files, move client API
