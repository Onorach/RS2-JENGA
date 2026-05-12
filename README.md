# Project JENGA: The Robotic Solver

## Overview

Project JENGA addresses two classic frustrations: finding a worthy Jenga opponent and enduring the tedious rebuild after every game. The solution pairs an Intel RealSense RGB-D camera with a UR3/UR3e collaborative robot to perceive, pick, and place blocks with precision — no human interaction required.

---

## Key Features / Subsystems

| Subsystem | Description |
|---|---|
| **Subsystem 1 — Perception and Mapping** | Accurately perceives Jenga block locations and the overall tower structure using a RealSense camera. |
| **Subsystem 2 — Motion Planning and Control** | Plans safe robot paths to ensure movement does not destabilise or collapse the tower. |
| **Subsystem 3 — Interaction and Execution** | Provides operator control via a GUI, including robot state monitoring, target block selection, and safety overrides. |

---

## Dependencies

### Hardware

- **Robot:** UR3 / UR3e Collaborative Robot
- **Camera:** Intel RealSense Camera
- **Gripper:** OnRobot Gripper
- **Miscellaneous:** Ethernet cable, Jenga game set, and a laptop with an Ethernet port

### Software

- **Operating System:** Linux
- **Robotic Framework:** ROS2 (Humble)
- **Version Control:** GitHub
- **Libraries:** `Tkinter`, `OpenCV`, `CvBridge`, `PIL/Pillow`, `std_srvs`

---

## Installation

### Hardware Setup

1. Mount the Intel RealSense Camera using the bracket to achieve a 3rd-person viewing position overlooking the work area.
2. Attach the OnRobot Gripper to the end of the UR3/UR3e robot arm.
3. Connect the robot to the laptop via Ethernet cable.

### Software Setup

```bash
# Clone the repository
git clone https://github.com/Onorach/RS2-JENGA.git
cd RS2-JENGA

# Install dependencies and build
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

---

## Running the System

Each command below must be run in a **separate terminal** after sourcing the workspace (`source install/setup.bash`).

**Step 1 — Launch the RealSense Camera Node:**
```bash
ros2 launch realsense2_camera rs_launch.py \
  depth_module.depth_profile:=640x480x30 \
  rgb_camera.color_profile:=640x480x30
```

**Step 2 — Launch Vision Processing (Perception):**
```bash
python3 src/perception/play_live.py
```

**Step 3 — Launch the JENGA Interface (GUI):**
```bash
python3 src/interaction_perception/GUI.py
```

### Expected Outcome

The GUI will launch with a banner titled **"JENGA Tower Interface"**, displaying:
- A live colour camera feed
- A robot state string (defaults to `"No Robot State received"`)
- A sidebar containing **Gripper Overrides**, **Next Goal** selection, and the **ESTOP** button

---

## Subsystem 3: Interaction and Execution

### Purpose

Acts as the central command hub for the operator to monitor robot status, select the next target block, and trigger emergency stops.

### Key Topics, Services & Files

| Type | Name | Detail |
|---|---|---|
| **Files** | `GUI.py` | Main interface |
| | `interaction_node` | ROS2 node backing the GUI |
| **Published Topics** | `/ee_override_array` | `Int8MultiArray` — gripper state overrides |
| | `/selected_goal` | `String/JSON` — currently selected block target |
| **Subscribed Topics** | `/camera/camera/color/image_raw` | Live camera feed |
| | `/robot_state` | Robot status strings |
| | `/top_layer_state` | Parsed tower JSON data |
| **Services** | `/estop` | `std_srvs/srv/SetBool` — halts all arm movement |

### Inputs & Outputs

- **Inputs:** Camera frames, robot status strings, parsed tower JSON data
- **Outputs:** `/estop` service calls to halt the robot; published arrays for gripper state overrides

### Independent Testing

1. **End-Effector Override** — Click `"Override to closed/opened"` and observe the robot end-effector move in simulation or on the physical arm.
2. **Camera Feed** — Change something in the camera's field of view and confirm the live feed updates inside the GUI.
3. **Goal Selection** — Click a block button in the **Next Goal** section and verify the goal position description updates on the GUI.
4. **Software ESTOP** — Click the ESTOP button and confirm the Robot State reflects the stop and that arm movement has paused in simulation or real life.

---

## Known Limitations

- **Service Dependency:** The ESTOP button will report `"Service not available"` if the motion control node providing the `/estop` server is not running.
- **USB 3.0 Requirement:** High-resolution RealSense streams require a USB 3.0 connection to avoid frame drop timeouts.