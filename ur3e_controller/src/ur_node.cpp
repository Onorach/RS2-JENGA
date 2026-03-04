#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.h>
#include <moveit/planning_scene_interface/planning_scene_interface.h>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <std_msgs/msg/int32.hpp>
#include <shape_msgs/msg/solid_primitive.hpp>
#include <geometric_shapes/solid_primitive_dims.h>
#include <moveit_msgs/msg/collision_object.hpp>
#include <moveit_msgs/msg/robot_trajectory.hpp>
#include <chrono>
#include <thread>
#include <atomic>
#include <algorithm>

class UR3eController : public rclcpp::Node
{
public:
    UR3eController() : Node("ur3e_controller")
    {
        // When true, use /clock from simulation (Gazebo); when false, use wall time (hardware).
        this->declare_parameter<bool>("use_sim_time", false);
        velocity_scaling_ = this->declare_parameter<double>("velocity_scaling", 0.5);

        // Clamp velocity scaling to a safe range (0.01, 1.0]
        if (velocity_scaling_ <= 0.0 || velocity_scaling_ > 1.0)
        {
            const double clamped = std::clamp(velocity_scaling_, 0.01, 1.0);
            RCLCPP_WARN(
                this->get_logger(),
                "Parameter 'velocity_scaling' out of range (%.3f). Clamping to %.3f.",
                velocity_scaling_,
                clamped);
            velocity_scaling_ = clamped;
        }

        planning_group_ = this->declare_parameter<std::string>("planning_group", "ur_manipulator");

        status_pub_ = this->create_publisher<std_msgs::msg::Int32>("/ur_status", 10);

        pose_sub_ = this->create_subscription<geometry_msgs::msg::PoseStamped>(
            "/move_group/goal", 10,
            std::bind(&UR3eController::poseCallback, this, std::placeholders::_1)
        );  
    }

    void initializeMoveGroup()
    {
        move_group_interface_ = std::make_shared<moveit::planning_interface::MoveGroupInterface>(
            std::static_pointer_cast<rclcpp::Node>(shared_from_this()), planning_group_
        );
        move_group_interface_->setMaxVelocityScalingFactor(velocity_scaling_);
        startupInitPose();

        // Add collision objects to the scene | Refer to function addCollisionObjects at line 110 for structure
        std::vector<std::vector<double>> objects =
        {
            {0.0, -0.35, 0.6, 0.0, 0.0, 0.0, 1.0, 1.2, 0.001, 1.2},  // Back Wall
            {0.0, 0.0, -0.005, 0.0, 0.0, 0.0, 1.0, 1.2, 1.2, 0.001} // Floor
        };
        addCollisionObjects(objects);

        RCLCPP_INFO(this->get_logger(), "Publishing ready status.");
        std_msgs::msg::Int32 ready_msg;
        ready_msg.data = 0; // Ready
        status_pub_->publish(ready_msg);
    }

private:
    enum StatusCode
    {
        STATUS_READY = 0,
        STATUS_EXECUTING = 1,
        STATUS_DONE = 2,
        STATUS_PLANNING_FAILED = 3,
        STATUS_EXECUTION_FAILED = 4
    };

    void startupInitPose()
    {
        std::vector<double> init_joint_positions = {1.8151, -1.1868, 1.50098, -1.8849, -1.5708, 0.0};
        move_group_interface_->setJointValueTarget(init_joint_positions);
        moveit::planning_interface::MoveGroupInterface::Plan plan;
        if (move_group_interface_->plan(plan))
        {
            RCLCPP_INFO(this->get_logger(), "Executing startup pose.");
            move_group_interface_->execute(plan);
        } else {
            RCLCPP_ERROR(this->get_logger(), "Failed to plan startup pose.");
        }
    }

    void poseCallback(const geometry_msgs::msg::PoseStamped::SharedPtr msg)
    {
        if (!move_group_interface_)
        {
            RCLCPP_ERROR(this->get_logger(), "MoveGroupInterface not initialized!");
            return;
        }

        // Do not accept a new goal while one is executing
        if (is_executing_)
        {
            RCLCPP_WARN(this->get_logger(), "Received goal while another is executing. Ignoring new goal.");
            return;
        }

        is_executing_ = true;

        RCLCPP_INFO(this->get_logger(), "Received new target pose.");

        std_msgs::msg::Int32 status_msg;
        status_msg.data = STATUS_EXECUTING;
        status_pub_->publish(status_msg);

        // Copy goal and keep node alive while executing in a worker thread
        auto goal = *msg;
        auto self = shared_from_this();

        std::thread([this, self, goal]() {
            executeGoal(goal);
        }).detach();
    }

    void executeGoal(const geometry_msgs::msg::PoseStamped &goal)
    {
        if (!move_group_interface_)
        {
            RCLCPP_ERROR(this->get_logger(), "MoveGroupInterface not initialized!");
            is_executing_ = false;
            return;
        }

        std_msgs::msg::Int32 status_msg;
        move_group_interface_->setStartStateToCurrentState();
        move_group_interface_->setPoseTarget(goal);

        moveit::planning_interface::MoveGroupInterface::Plan plan;
        auto planning_result = move_group_interface_->plan(plan);

        if (planning_result != moveit::core::MoveItErrorCode::SUCCESS)
        {
            RCLCPP_ERROR(this->get_logger(), "Planning failed with error code: %d", planning_result.val);
            status_msg.data = STATUS_PLANNING_FAILED;
            status_pub_->publish(status_msg);
        }
        else
        {
            auto result = move_group_interface_->execute(plan);
            status_msg.data = (result == moveit::core::MoveItErrorCode::SUCCESS)
                                  ? STATUS_DONE
                                  : STATUS_EXECUTION_FAILED;
            status_pub_->publish(status_msg);
        }

        // Publish ready status AFTER execution or error
        std_msgs::msg::Int32 ready_msg;
        ready_msg.data = STATUS_READY;
        status_pub_->publish(ready_msg);

        is_executing_ = false;
    }

    void addCollisionObjects(const std::vector<std::vector<double>> &object_specs)
    {
        moveit::planning_interface::PlanningSceneInterface planning_scene_interface;
        std::vector<moveit_msgs::msg::CollisionObject> collision_objects;

        for (size_t i = 0; i < object_specs.size(); ++i)
        {
            const auto &spec = object_specs[i];
            if (spec.size() != 10) continue;

            moveit_msgs::msg::CollisionObject object;
            object.header.frame_id = "base_link";
            object.id = "object_" + std::to_string(i);

            shape_msgs::msg::SolidPrimitive primitive;
            primitive.type = primitive.BOX;
            primitive.dimensions = {spec[7], spec[8], spec[9]}; //x,y,z Dimensions

            geometry_msgs::msg::Pose pose; //x,y,z and Quaternian for defining pose of object centre
            pose.position.x = spec[0];
            pose.position.y = spec[1];
            pose.position.z = spec[2];
            pose.orientation.x = spec[3];
            pose.orientation.y = spec[4];
            pose.orientation.z = spec[5];
            pose.orientation.w = spec[6];

            object.primitives.push_back(primitive);
            object.primitive_poses.push_back(pose);
            object.operation = object.ADD;

            collision_objects.push_back(object);
        }

        planning_scene_interface.applyCollisionObjects(collision_objects);
        RCLCPP_INFO(this->get_logger(), "Added %zu collision objects.", collision_objects.size());
    }

    rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr pose_sub_;
    rclcpp::Publisher<std_msgs::msg::Int32>::SharedPtr status_pub_;
    std::shared_ptr<moveit::planning_interface::MoveGroupInterface> move_group_interface_;
    std::string planning_group_;
    double velocity_scaling_;
    std::atomic<bool> is_executing_{false};
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<UR3eController>();
    node->initializeMoveGroup();
    rclcpp::spin(node);
    rclcpp::shutdown();
}
