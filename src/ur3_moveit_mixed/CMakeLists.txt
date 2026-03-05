cmake_minimum_required(VERSION 3.8)
project(ur3_moveit_mixed)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)
find_package(moveit_core REQUIRED)
find_package(geometry_msgs REQUIRED)

# ==========================================
# C++ Setup
# ==========================================
add_executable(ur3_cpp_node src/ur3_cpp_node.cpp)
target_include_directories(ur3_cpp_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)
target_compile_features(ur3_cpp_node PUBLIC cxx_std_17)

ament_target_dependencies(ur3_cpp_node
  rclcpp
  moveit_ros_planning_interface
  moveit_core
  geometry_msgs
)

install(TARGETS ur3_cpp_node
  DESTINATION lib/${PROJECT_NAME}
)

# ==========================================
# Python Setup
# ==========================================
# Install Python executable scripts
install(PROGRAMS
  scripts/ur3_py_node.py
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch files and other assets
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
