# jenga_interfaces

ROS 2 interface definitions for Jenga manipulation: **actions** used by MoveIt Task Constructor (MTC) servers in `mtc_jenga_servers`, and a **service** used by `motion_planning` / `jenga_blocks_scene` for planning-scene-only tests.

## Build

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select jenga_interfaces
source install/setup.bash
```

Depend on this package in `package.xml` with `<depend>jenga_interfaces</depend>` (or `build_depend` / `exec_depend` as appropriate).

## Actions

Source files live under `action/`. Generated Python/C++ types follow `jenga_interfaces/action/<Name>.action`.

| Action | Purpose (summary) |
|--------|-------------------|
| `JengaPickPlace` | Pick at `pick_pose`, place at `place_pose`; `block_index` labels the step. |
| `JengaArmReady` | Move arm to a named SRDF state (optional `target_state`; empty uses server default). |
| `JengaExtractSideBlock` | Extract a block from the side of the tower; `block_pose`, `place_pose`, `block_index`. |
| `JengaExtractMiddleBlock` | Extract from the middle; includes `extract_axis` (e.g. `"x"`, `"-x"`; empty → server auto-detect). |
| `JengaProbeBlock` | FT-guided probe; result includes `probe_outcome`, `score`, `displacement_m`, `max_force_n`. |

Each action follows the usual ROS 2 pattern: **Goal**, **Result** (`success`, `message`, `error_code`, plus action-specific fields), **Feedback** (`current_stage`, `progress_pct`).

See the `.action` files for exact field types:

- [`action/JengaPickPlace.action`](action/JengaPickPlace.action)
- [`action/JengaArmReady.action`](action/JengaArmReady.action)
- [`action/JengaExtractSideBlock.action`](action/JengaExtractSideBlock.action)
- [`action/JengaExtractMiddleBlock.action`](action/JengaExtractMiddleBlock.action)
- [`action/JengaProbeBlock.action`](action/JengaProbeBlock.action)

## Services

| Service | File | Purpose |
|---------|------|---------|
| `ProtrudeJengaBlock` | [`srv/ProtrudeJengaBlock.srv`](srv/ProtrudeJengaBlock.srv) | Shift a block collision object in the planning scene by `distance_m` along `axis` for `block_index` (planning scene only). |

Implemented by `jenga_blocks_scene` in `motion_planning` as `protrude_jenga_block`.

## Usage from code

After sourcing the workspace:

```python
from jenga_interfaces.action import JengaPickPlace, JengaArmReady
from jenga_interfaces.srv import ProtrudeJengaBlock
```

## See also

- [motion_planning README](../motion_planning/README.md) – MTC bringup, calling actions, tests, sequencers
- [mtc_jenga_servers README](../mtc_jenga_servers/README.md) – C++ action servers and default action names
