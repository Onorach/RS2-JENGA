## ur3_moveit_mixed

High-level control package for a UR3e robot using MoveIt 2 on ROS 2 Humble.
It provides:

- **RViz-only simulation** using MoveIt fake controllers.
- **Hardware-ready MoveIt bringup** that can be used together with `ur_robot_driver`.
- Example **C++** and **Python** demo nodes.

### Build

From the workspace root:

```bash
colcon build --packages-select ur3_moveit_mixed
source install/setup.bash
```

### RViz/MoveIt simulation

Launch the UR3e with MoveIt and RViz, using fake controllers:

```bash
ros2 launch ur3_moveit_mixed ur3_demo.launch.py
```

Notes:

- Set `use_rviz:=false` if you want a headless MoveIt bringup:

  ```bash
  ros2 launch ur3_moveit_mixed ur3_demo.launch.py use_rviz:=false
  ```

- The MoveIt RViz MotionPlanning plugin is preconfigured for the `ur_manipulator`
  planning group and the `world` fixed frame.

### C++ MoveIt demo node

The C++ node `ur3_cpp_node` uses `MoveGroupInterface` to plan to a hard-coded pose
and execute it once.

It is started automatically by `ur3_demo.launch.py`. You should see log output like:

- Planning succeeded / failed.
- Execution result status.

If you want to run it separately (with MoveIt already running):

```bash
ros2 run ur3_moveit_mixed ur3_cpp_node
```

### Python FollowJointTrajectory demo

The Python script `ur3_py_node.py` sends a `FollowJointTrajectory` goal to the
MoveIt fake controller `fake_arm_controller`:

```bash
ros2 run ur3_moveit_mixed ur3_py_node.py
```

Make sure `ur3_demo.launch.py` is running so that the fake controller and MoveIt
are available. The demo sends a single joint-space trajectory and then exits.

### Hardware-ready MoveIt bringup

Once you have `ur_robot_driver` configured and talking to your UR3e, you can start
a MoveIt bringup that is configured for real controllers:

```bash
ros2 launch ur3_moveit_mixed ur3_hardware.launch.py
```

This launch file:

- Uses the same `ur_moveit_config` and `ur_description` setup as the simulation launch.
- Loads controller configuration from `config/hardware_controllers.yaml`, which assumes
  a `scaled_joint_trajectory_controller` exposing a FollowJointTrajectory action.

You typically run the hardware bringup **in addition to** the `ur_robot_driver`
bringup launch that starts the actual robot hardware and ros2_control stack.

