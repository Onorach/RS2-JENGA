# Project JENGA: The Robotic Solver

## Project Overview
[cite_start]Project JENGA addresses the challenge of finding a coordinated opponent for Jenga and the tedious process of rebuilding the tower[cite: 8, 9]. [cite_start]The solution utilizes a UR3/UR3e robot and a 3rd-person viewing RGB-D camera to autonomously perceive, pick, and place blocks with precision and no human interaction[cite: 12].

## Key Features / Subsystems
* [cite_start]**Subsystem 1 - Perception and Mapping:** Accurately perceives Jenga block locations and the overall tower using a RealSense camera[cite: 16, 47].
* [cite_start]**Subsystem 2 - Motion Planning and Control:** Plots safe, collision-free paths for the robot to ensure movement does not collapse the tower[cite: 19, 47].
* [cite_start]**Subsystem 3 - Interaction and Execution:** Provides user control via a GUI, including robot state monitoring, target selection, and safety overrides.

## Dependencies

### Hardware (Bill of Materials)
* [cite_start]**Robot**: UR3/UR3e Collaborative Robot[cite: 12, 43].
* [cite_start]**Camera**: Intel RealSense RGB-D Camera[cite: 12, 43].
* [cite_start]**Gripper**: OnRobot Gripper[cite: 43].
* [cite_start]**Miscellaneous**: Ethernet cable, Jenga Game, and a laptop with an Ethernet connection[cite: 43].

### Software
* [cite_start]**Operating System**: Linux[cite: 43].
* [cite_start]**Robotic Framework**: ROS2 Humble[cite: 43].
* [cite_start]**Version Control**: GitHub[cite: 43].
* **Libraries**: `Tkinter` (GUI), `OpenCV`, `CvBridge`, `PIL/Pillow`, and `std_srvs`.

---

## Installation

### Hardware Setup
1. [cite_start]Mount the Intel RealSense Camera with the bracket providing a 3rd-person viewing position overlooking the work area[cite: 12].
2. [cite_start]Attach the **OnRobot Gripper** to the UR3/UR3e robot arm[cite: 43].
3. [cite_start]Connect the robot to the laptop via **Ethernet**[cite: 43].

### Software Setup
```bash
# Clone the repository
git clone [https://github.com/Onorach/RS2-JENGA.git](https://github.com/Onorach/RS2-JENGA.git)
cd RS2-JENGA

# Install dependencies and build
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash