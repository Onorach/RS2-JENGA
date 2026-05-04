cmake_minimum_required(VERSION 3.16)
project(mtc_pick_place)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(ament_cmake REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(jenga_interfaces REQUIRED)
find_package(moveit_msgs REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)
find_package(moveit_task_constructor_core REQUIRED)
find_package(moveit_task_constructor_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(shape_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(tf2_eigen REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)

add_executable(mtc_pick_place_server src/mtc_pick_place_server.cpp)
target_include_directories(mtc_pick_place_server PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:include>)
ament_target_dependencies(mtc_pick_place_server
  geometry_msgs
  jenga_interfaces
  moveit_msgs
  moveit_ros_planning_interface
  moveit_task_constructor_core
  moveit_task_constructor_msgs
  rclcpp
  rclcpp_action
  shape_msgs
  std_msgs
  tf2_eigen
  tf2_geometry_msgs
)

add_executable(mtc_extract_side_block_server src/mtc_extract_side_block_server.cpp)
target_include_directories(mtc_extract_side_block_server PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:include>)
ament_target_dependencies(mtc_extract_side_block_server
  geometry_msgs
  jenga_interfaces
  moveit_msgs
  moveit_ros_planning_interface
  moveit_task_constructor_core
  moveit_task_constructor_msgs
  rclcpp
  rclcpp_action
  shape_msgs
  std_msgs
  tf2_eigen
  tf2_geometry_msgs
)

add_executable(mtc_extract_middle_block_server src/mtc_extract_middle_block_server.cpp)
target_include_directories(mtc_extract_middle_block_server PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:include>)
ament_target_dependencies(mtc_extract_middle_block_server
  geometry_msgs
  jenga_interfaces
  moveit_msgs
  moveit_ros_planning_interface
  moveit_task_constructor_core
  moveit_task_constructor_msgs
  rclcpp
  rclcpp_action
  shape_msgs
  std_msgs
  tf2_eigen
  tf2_geometry_msgs
)

add_executable(mtc_probe_block_server src/mtc_probe_block_server.cpp)
target_include_directories(mtc_probe_block_server PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:include>)
ament_target_dependencies(mtc_probe_block_server
  geometry_msgs
  jenga_interfaces
  moveit_msgs
  moveit_ros_planning_interface
  moveit_task_constructor_core
  moveit_task_constructor_msgs
  rclcpp
  rclcpp_action
  shape_msgs
  std_msgs
  tf2_eigen
  tf2_geometry_msgs
)

install(TARGETS mtc_pick_place_server DESTINATION lib/${PROJECT_NAME})
install(TARGETS
  mtc_extract_side_block_server
  mtc_extract_middle_block_server
  mtc_probe_block_server
  DESTINATION lib/${PROJECT_NAME}
)
install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})
install(DIRECTORY config DESTINATION share/${PROJECT_NAME})
install(DIRECTORY resource DESTINATION share/${PROJECT_NAME})
install(DIRECTORY include/ DESTINATION include)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
