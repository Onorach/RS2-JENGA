# RS2 Jenga Project Readme

## Start the Environment (Choose ONE option)
---

### Option 1: Gazebo Classic

#### Step 1: Launch Gazebo and Moveit

    Ensure your workspace is built and activated

'''
    cd ~/ros2_ws
    source install/setup.bash
'''

    Launch Gazebo and Moveit

    ros2 launch ur_simulation_gazebo ur_sim_moveit.launch.py

    Note: The launch defaults to a ur5e, make sure to go into the launch files and edit them to default to ur3e.


### Option 2: Real Robot
#### Step 1: Launch UR3e Driver and Visualization (Real Robot)
##### 1. Setup the robot for external control

    On the robot tablet:
        Press the red button (power off) on the bottom left; if this is your first time starting, click "confirm configuration" on the pop-up.
        Press "On".
        Press "Start" when it becomes available.
        Press "Exit".
        Navigate to "Program" -> Urcaps.
        Press on "External Control" once.

##### 2. Launch the UR3e driver and RViz

'''
source /opt/ros/iron/setup.bash
ros2 launch ur_robot_driver ur_control.launch.py ur_type:=ur3e robot_ip:=192.168.56.101 launch_rviz:=true
'''

##### 3. Setup the robot for external control

    Go back to the tablet:
        Press on the start/pause button on the bottom right of the screen, on the left of "Simulation".
        Press on "Play from selection #: Control by Desktop".

##### 4. AFTER you finish with the robot

    Go back to the tablet:
        Press the green button on the bottom left (normal)
        Press on the red "Off" button
        Press the metal on/off button on the tablet to shut down, click "do not save" if prompted

## Executing the Code
---
### Step 1: Build and Source

    In a new terminal
'''
    source /opt/ros/iron/setup.bash
    colcon build --packages-select ur3e_controller
    source install/setup.bash
'''

### Step 2: Launch Moveit2


#### 1. If using the real robot

    Complete the corresponding steps from Option 1 or Option 3.

'''
ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur3e launch_rviz:=true
'''

#### 2. If using Gazebo

    If you completed the corresponding steps from Option 2, it should already be running, if not.

'''
ros2 launch ur_simulation_gazebo ur_sim_moveit.launch.py
'''

### Step 3: Launch a Demo

    In a new terminal, repeat step 1, then finally, run your package

'''
    ros2 run rs2_jenga initials_demo
'''
    (Or: ros2 run rs2_jenga move_ur3e_demo)

## Running Simulation
---

ros2 launch ur_simulation_gazebo ur_sim_control.launch.py

Move robot using test script from ur_robot_driver package (if you've installed that one):

ros2 launch ur_robot_driver test_joint_trajectory_controller.launch.py

Example using MoveIt with simulated robot:

ros2 launch ur_simulation_gazebo ur_sim_moveit.launch.py
