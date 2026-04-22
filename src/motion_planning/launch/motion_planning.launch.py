
"""
Launch Motion Planning and Control: pose goal node, exclusion zones, and e-stop node.
Start this after MoveIt2 and the robot (sim or hardware) are running.

planner:=rmrc (default) runs the DIY RMRC planning node (no MoveIt needed).
planner:=moveit runs the MoveIt OMPL pose_goal_node.
planner:=moveit_cartesian runs the MoveIt Cartesian node (straight-line first,
OMPL fallback on collision).

Both MoveIt planners require move_group to be running (e.g. via ur_moveit_config).
RMRC needs robot_description, built from the same workspace xacro as
ur3e_sim_control (ur3e_workspace.urdf.xacro).
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
    PythonExpression,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_planning = "motion_planning"
    pkg_controller = "ur3e_controller"

    exclusion_zones_file_arg = DeclareLaunchArgument(
        "exclusion_zones_file",
        default_value=PathJoinSubstitution(
            [FindPackageShare(pkg_planning), "config", "ur3e_workspace.yaml"]
        ),
        description=(
            "Absolute path to a YAML file defining exclusion zones to load into the "
            "MoveIt2 planning scene. Defaults to ur3e_workspace.yaml (cabinet, platform, "
            "Jenga tower in base_link with cabinet top at z=0, matching default base_height). "
            "Pass an empty string to load no YAML zones."
        ),
    )
    add_floor_plane_arg = DeclareLaunchArgument(
        "add_floor_plane",
        default_value="false",
        description=(
            "If true, publish the built-in floor-plane slab on startup. Default is false so the "
            "slab is not placed in the wrong frame; add it from robot_gui (or set this to true "
            "with floor_plane_frame_id:=world when you want it at launch)."
        ),
    )
    floor_z_arg = DeclareLaunchArgument(
        "floor_z",
        default_value="0.0",
        description=(
            "Z height (metres) of the floor-plane slab top surface in floor_plane_frame_id. "
            "0.0 = ground plane when using world frame."
        ),
    )
    floor_plane_frame_id_arg = DeclareLaunchArgument(
        "floor_plane_frame_id",
        default_value="world",
        description=(
            "TF frame for the floor-plane collision object. "
            "'world' places it at the global ground; 'base_link' places it relative to the robot."
        ),
    )
    plan_only_arg = DeclareLaunchArgument(
        "plan_only",
        default_value="false",
        description="If true, pose_goal_node only plans and does not execute.",
    )
    move_action_arg = DeclareLaunchArgument(
        "move_action_name",
        default_value="/move_action",
        description="MoveGroup action name (from MoveIt2 move_group).",
    )
    joint_action_arg = DeclareLaunchArgument(
        "joint_trajectory_action",
        default_value="/joint_trajectory_controller/follow_joint_trajectory",
        description="FollowJointTrajectory action used by estop_node to cancel all goals.",
    )
    planner_arg = DeclareLaunchArgument(
        "planner",
        default_value="rmrc",
        choices=["rmrc", "moveit", "moveit_cartesian"],
        description=(
            "Planning backend: 'rmrc' (DIY RMRC), 'moveit' (OMPL via MoveGroup), "
            "'moveit_cartesian' (Cartesian straight-line + OMPL fallback)."
        ),
    )
    max_step_arg = DeclareLaunchArgument(
        "max_step",
        default_value="0.005",
        description=(
            "moveit_cartesian: maximum Cartesian distance (m) between consecutive "
            "trajectory points.  Smaller = smoother but slower to compute."
        ),
    )
    jump_threshold_arg = DeclareLaunchArgument(
        "jump_threshold",
        default_value="5.0",
        description=(
            "moveit_cartesian: joint-space jump filter.  Steps where any joint "
            "moves more than this factor times the average step are truncated."
        ),
    )
    cartesian_fraction_threshold_arg = DeclareLaunchArgument(
        "cartesian_fraction_threshold",
        default_value="1.0",
        description=(
            "moveit_cartesian: minimum fraction of the Cartesian path that must "
            "be collision-free to accept it.  1.0 = require full path, else OMPL fallback."
        ),
    )
    max_velocity_scaling_factor_arg = DeclareLaunchArgument(
        "max_velocity_scaling_factor",
        default_value="0.1",
        description="moveit_cartesian: scale factor (0,1] for maximum joint velocities.",
    )
    max_acceleration_scaling_factor_arg = DeclareLaunchArgument(
        "max_acceleration_scaling_factor",
        default_value="0.1",
        description="moveit_cartesian: scale factor (0,1] for maximum joint accelerations.",
    )
    exec_start_delay_arg = DeclareLaunchArgument(
        "execution_start_delay",
        default_value="0.5",
        description=(
            "Delay (seconds) added to all RMRC trajectory timestamps before execution "
            "to avoid controller path/state tolerance violations at trajectory start."
        ),
    )
    goal_time_tolerance_arg = DeclareLaunchArgument(
        "goal_time_tolerance",
        default_value="2.0",
        description=(
            "Extra allowed time (seconds) for RMRC joint_trajectory_controller goal convergence."
        ),
    )
    max_joint_velocity_arg = DeclareLaunchArgument(
        "max_joint_velocity",
        default_value="0.25",
        description=(
            "RMRC-only: absolute per-joint velocity limit in rad/s for generated trajectories."
        ),
    )
    max_joint_acceleration_arg = DeclareLaunchArgument(
        "max_joint_acceleration",
        default_value="0.5",
        description=(
            "RMRC-only: absolute per-joint acceleration limit in rad/s^2 for generated trajectories."
        ),
    )
    execution_mode_arg = DeclareLaunchArgument(
        "execution_mode",
        default_value="trajectory",
        description=(
            "RMRC execution mode: 'trajectory' sends FollowJointTrajectory goals, "
            "'velocity' streams joint velocities to a velocity controller topic."
        ),
    )
    kinematics_backend_arg = DeclareLaunchArgument(
        "kinematics_backend",
        default_value="hybrid",
        description=(
            "RMRC kinematics backend: 'pykdl' for FK/Jacobian only, "
            "'hybrid' enables PyKDL + optional analytical IK helper."
        ),
    )
    velocity_command_topic_arg = DeclareLaunchArgument(
        "velocity_command_topic",
        default_value="/joint_group_velocity_controller/commands",
        description="Topic used for RMRC velocity streaming mode.",
    )
    ik_seed_gain_arg = DeclareLaunchArgument(
        "ik_seed_gain",
        default_value="0.0",
        description=(
            "Null-space gain toward analytical IK seed in RMRC planning. "
            "Set >0 only when analytical IK backend is available."
        ),
    )
    body_link_weight_arg = DeclareLaunchArgument(
        "body_link_weight",
        default_value="0.55",
        description=(
            "RMRC: scale for repulsion at intermediate link frames (upper_arm, forearm, etc.). "
            "Higher values push the middle of the arm away from exclusion zones."
        ),
    )
    max_cart_repulsion_linear_arg = DeclareLaunchArgument(
        "max_cart_repulsion_linear",
        default_value="0.75",
        description="RMRC: cap on repulsion linear velocity magnitude (m/s) blended into task.",
    )
    use_multi_point_repulsion_arg = DeclareLaunchArgument(
        "use_multi_point_repulsion",
        default_value="true",
        description="RMRC: if true, repulsion uses EE plus sampled link origins (PyKDL).",
    )
    posture_bias_gain_arg = DeclareLaunchArgument(
        "posture_bias_gain",
        default_value="0.0",
        description=(
            "RMRC: null-space gain toward merged posture targets (shoulder/elbow). "
            "Set >0 together with posture_apply_* to reduce inverted-V toward cabinet."
        ),
    )
    posture_apply_shoulder_lift_arg = DeclareLaunchArgument(
        "posture_apply_shoulder_lift",
        default_value="false",
        description="RMRC: apply posture_shoulder_lift_target_rad in null space.",
    )
    posture_apply_elbow_arg = DeclareLaunchArgument(
        "posture_apply_elbow",
        default_value="false",
        description="RMRC: apply posture_elbow_target_rad in null space.",
    )
    ik_score_mode_arg = DeclareLaunchArgument(
        "ik_score_mode",
        default_value="composite",
        description=(
            "RMRC analytical IK branch: nearest | elbow_up | clearance | composite "
            "(elbow + link clearance − start distance)."
        ),
    )
    ik_score_w_elbow_arg = DeclareLaunchArgument(
        "ik_score_w_elbow",
        default_value="1.0",
        description="RMRC composite IK: weight on elbow_joint (higher = elbow-up preference).",
    )
    ik_score_w_clearance_arg = DeclareLaunchArgument(
        "ik_score_w_clearance",
        default_value="0.08",
        description="RMRC composite IK: weight on sum of link–obstacle distances.",
    )
    ik_score_w_start_arg = DeclareLaunchArgument(
        "ik_score_w_start",
        default_value="0.35",
        description="RMRC composite IK: penalty weight on ||q_ik − q_start||.",
    )
    joint_secondary_weight_arg = DeclareLaunchArgument(
        "joint_secondary_weight",
        default_value="0.0",
        description=(
            "RMRC: shoulder/elbow secondary strength (0 disables). "
            "Internal diagonal uses weight * joint_secondary_w_epsilon so Cartesian dominates."
        ),
    )
    joint_secondary_gain_arg = DeclareLaunchArgument(
        "joint_secondary_gain",
        default_value="1.5",
        description="RMRC: gain on (q_bias − q) for shoulder_lift and elbow in joint secondary.",
    )
    joint_secondary_w_epsilon_arg = DeclareLaunchArgument(
        "joint_secondary_w_epsilon",
        default_value="0.025",
        description=(
            "RMRC: scales Wdiag = joint_secondary_weight * epsilon (keep subordinate to JᵀJ)."
        ),
    )
    joint_secondary_pref_clip_arg = DeclareLaunchArgument(
        "joint_secondary_pref_clip",
        default_value="0.45",
        description="RMRC: clip |gain * (q_bias − q)| per joint (rad/s scale) for joint secondary.",
    )
    repulsion_smooth_alpha_arg = DeclareLaunchArgument(
        "repulsion_smooth_alpha",
        default_value="0.45",
        description="RMRC: EMA on repulsion Cartesian vector (1.0 = no smoothing).",
    )
    repulsion_dist_scale_arg = DeclareLaunchArgument(
        "repulsion_dist_scale",
        default_value="true",
        description="RMRC: scale repulsion gain by normalized distance inside influence zone.",
    )
    repulsion_out_grad_cap_arg = DeclareLaunchArgument(
        "repulsion_out_grad_cap",
        default_value="120.0",
        description="RMRC: cap on repulsion gradient magnitude (0 = no cap).",
    )
    orientation_error_gain_arg = DeclareLaunchArgument(
        "orientation_error_gain",
        default_value="1.15",
        description="RMRC: multiply orientation path/hold error (EE-down tracking).",
    )
    path_fb_scale_cap_arg = DeclareLaunchArgument(
        "path_fb_scale_cap",
        default_value="2.5",
        description="RMRC: cap on Cartesian path feedback gain (0 = no cap).",
    )
    publish_world_to_base_tf_arg = DeclareLaunchArgument(
        "publish_world_to_base_tf",
        default_value="false",
        description=(
            "If true, publish static TF world->base_link. Keep false when using "
            "ur3e_sim_control (workspace URDF already publishes this transform)."
        ),
    )
    base_height_arg = DeclareLaunchArgument(
        "base_height",
        default_value="1.080",
        description=(
            "Z translation for world->base_link static TF (metres). Must match robot spawn height."
        ),
    )

    # robot_description for RMRC: same workspace xacro as ur3e_sim_control (single world->base TF)
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare(pkg_controller), "urdf", "ur3e_workspace.urdf.xacro"]
            ),
            " ",
            "safety_limits:=true",
            " ",
            "safety_pos_margin:=0.15",
            " ",
            "safety_k_position:=20",
            " ",
            "name:=ur",
            " ",
            "ur_type:=ur3e",
            " ",
            'prefix:=""',
            " ",
            "sim_gazebo:=true",
            " ",
            "simulation_controllers:=",
            PathJoinSubstitution(
                [FindPackageShare(pkg_controller), "config", "ur3e_controllers.yaml"]
            ),
            " ",
            "initial_positions_file:=",
            PathJoinSubstitution(
                [FindPackageShare("ur_description"), "config", "initial_positions.yaml"]
            ),
            " ",
            "base_height:=",
            LaunchConfiguration("base_height"),
        ]
    )

    pose_goal_node = Node(
        package=pkg_planning,
        executable="pose_goal_node",
        name="pose_goal_node",
        output="screen",
        condition=IfCondition(
            PythonExpression(["'", LaunchConfiguration("planner"), "' == 'moveit'"])
        ),
        parameters=[
            {
                "plan_only": LaunchConfiguration("plan_only"),
                "move_action_name": LaunchConfiguration("move_action_name"),
            },
        ],
    )

    moveit_cartesian_node = Node(
        package=pkg_planning,
        executable="moveit_cartesian_node",
        name="moveit_cartesian_node",
        output="screen",
        condition=IfCondition(
            PythonExpression(
                ["'", LaunchConfiguration("planner"), "' == 'moveit_cartesian'"]
            )
        ),
        parameters=[
            {
                "plan_only": LaunchConfiguration("plan_only"),
                "move_action_name": LaunchConfiguration("move_action_name"),
                "joint_trajectory_action": LaunchConfiguration(
                    "joint_trajectory_action"
                ),
                "max_step": LaunchConfiguration("max_step"),
                "jump_threshold": LaunchConfiguration("jump_threshold"),
                "cartesian_fraction_threshold": LaunchConfiguration(
                    "cartesian_fraction_threshold"
                ),
                "max_velocity_scaling_factor": LaunchConfiguration(
                    "max_velocity_scaling_factor"
                ),
                "max_acceleration_scaling_factor": LaunchConfiguration(
                    "max_acceleration_scaling_factor"
                ),
            },
        ],
    )

    rmrc_planning_node = Node(
        package=pkg_planning,
        executable="rmrc_planning_node",
        name="rmrc_planning_node",
        output="screen",
        condition=IfCondition(
            PythonExpression(["'", LaunchConfiguration("planner"), "' == 'rmrc'"])
        ),
        parameters=[
            {
                "robot_description": robot_description_content,
                "exclusion_zones_file": LaunchConfiguration("exclusion_zones_file"),
                "plan_only": LaunchConfiguration("plan_only"),
                "joint_trajectory_action": LaunchConfiguration("joint_trajectory_action"),
                "path_resolution": 0.002,
                "max_velocity": 0.2,
                "d_safe": 0.065,
                "k_repulsion": 0.55,
                "execution_start_delay": LaunchConfiguration("execution_start_delay"),
                "goal_time_tolerance": LaunchConfiguration("goal_time_tolerance"),
                "max_joint_velocity": LaunchConfiguration("max_joint_velocity"),
                "max_joint_acceleration": LaunchConfiguration("max_joint_acceleration"),
                "execution_mode": LaunchConfiguration("execution_mode"),
                "kinematics_backend": LaunchConfiguration("kinematics_backend"),
                "velocity_command_topic": LaunchConfiguration("velocity_command_topic"),
                "ik_seed_gain": LaunchConfiguration("ik_seed_gain"),
                "body_link_weight": LaunchConfiguration("body_link_weight"),
                "max_cart_repulsion_linear": LaunchConfiguration("max_cart_repulsion_linear"),
                "use_multi_point_repulsion": LaunchConfiguration("use_multi_point_repulsion"),
                "posture_bias_gain": LaunchConfiguration("posture_bias_gain"),
                "posture_apply_shoulder_lift": LaunchConfiguration("posture_apply_shoulder_lift"),
                "posture_apply_elbow": LaunchConfiguration("posture_apply_elbow"),
                "ik_score_mode": LaunchConfiguration("ik_score_mode"),
                "ik_score_w_elbow": LaunchConfiguration("ik_score_w_elbow"),
                "ik_score_w_clearance": LaunchConfiguration("ik_score_w_clearance"),
                "ik_score_w_start": LaunchConfiguration("ik_score_w_start"),
                "joint_secondary_weight": LaunchConfiguration("joint_secondary_weight"),
                "joint_secondary_gain": LaunchConfiguration("joint_secondary_gain"),
                "joint_secondary_w_epsilon": LaunchConfiguration("joint_secondary_w_epsilon"),
                "joint_secondary_pref_clip": LaunchConfiguration("joint_secondary_pref_clip"),
                "repulsion_smooth_alpha": LaunchConfiguration("repulsion_smooth_alpha"),
                "repulsion_dist_scale": LaunchConfiguration("repulsion_dist_scale"),
                "repulsion_out_grad_cap": LaunchConfiguration("repulsion_out_grad_cap"),
                "orientation_error_gain": LaunchConfiguration("orientation_error_gain"),
                "path_fb_scale_cap": LaunchConfiguration("path_fb_scale_cap"),
            },
        ],
    )

    world_to_base_tf_node = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="world_to_base_link_motion_planning",
        output="screen",
        arguments=[
            "0",
            "0",
            LaunchConfiguration("base_height"),
            "0",
            "0",
            "0",
            "world",
            "base_link",
        ],
        condition=IfCondition(LaunchConfiguration("publish_world_to_base_tf")),
    )

    exclusion_zones_node = Node(
        package=pkg_planning,
        executable="exclusion_zones_node",
        name="exclusion_zones_node",
        output="screen",
        parameters=[
            {
                "exclusion_zones_file": LaunchConfiguration("exclusion_zones_file"),
                "add_floor_plane": LaunchConfiguration("add_floor_plane"),
                "floor_z": LaunchConfiguration("floor_z"),
                "floor_plane_frame_id": LaunchConfiguration("floor_plane_frame_id"),
            },
        ],
    )

    estop_node = Node(
        package=pkg_controller,
        executable="estop_node",
        name="estop_node",
        output="screen",
        parameters=[
            {
                "joint_trajectory_action": LaunchConfiguration("joint_trajectory_action"),
            },
        ],
    )

    return LaunchDescription([
        exclusion_zones_file_arg,
        add_floor_plane_arg,
        floor_z_arg,
        floor_plane_frame_id_arg,
        plan_only_arg,
        move_action_arg,
        joint_action_arg,
        planner_arg,
        max_step_arg,
        jump_threshold_arg,
        cartesian_fraction_threshold_arg,
        max_velocity_scaling_factor_arg,
        max_acceleration_scaling_factor_arg,
        exec_start_delay_arg,
        goal_time_tolerance_arg,
        max_joint_velocity_arg,
        max_joint_acceleration_arg,
        execution_mode_arg,
        kinematics_backend_arg,
        velocity_command_topic_arg,
        ik_seed_gain_arg,
        body_link_weight_arg,
        max_cart_repulsion_linear_arg,
        use_multi_point_repulsion_arg,
        posture_bias_gain_arg,
        posture_apply_shoulder_lift_arg,
        posture_apply_elbow_arg,
        ik_score_mode_arg,
        ik_score_w_elbow_arg,
        ik_score_w_clearance_arg,
        ik_score_w_start_arg,
        joint_secondary_weight_arg,
        joint_secondary_gain_arg,
        joint_secondary_w_epsilon_arg,
        joint_secondary_pref_clip_arg,
        repulsion_smooth_alpha_arg,
        repulsion_dist_scale_arg,
        repulsion_out_grad_cap_arg,
        orientation_error_gain_arg,
        path_fb_scale_cap_arg,
        publish_world_to_base_tf_arg,
        base_height_arg,
        world_to_base_tf_node,
        pose_goal_node,
        moveit_cartesian_node,
        rmrc_planning_node,
        exclusion_zones_node,
        estop_node,
    ])
